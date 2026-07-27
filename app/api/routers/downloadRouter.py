from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.apiSchemas import (
    DownloadBatchRequest,
    DownloadBatchResponse,
    DownloadResponse,
    TaskResponse,
)
from app.api.dependencies import (
    createApiRepositoryRegistry,
    getSession,
    getTaskManager,
)
from app.api.errors import ApiError
from app.application.use_cases.downloads import DownloadAudioUseCase
from app.config.settings import get_settings
from app.infrastructure.downloads.youtube import YtDlpAudioDownloader
from app.infrastructure.metadata import MutagenLocalSongMetadataReader
from app.infrastructure.tasks import LocalTaskManager, TaskContext

router = APIRouter(prefix="/downloads", tags=["downloads"])


@dataclass(frozen=True, slots=True)
class _DownloadSource:
    source_url: str
    youtube_playlist_item_id: int | None = None
    source_title: str | None = None
    source_artist: str | None = None


@router.get("", response_model=list[DownloadResponse])
def listDownloads(
    limit: int = 100,
    session: Session = Depends(getSession),
) -> list:
    if limit <= 0 or limit > 500:
        raise ValueError("El limite de descargas debe estar entre 1 y 500.")
    registry = createApiRepositoryRegistry(session)
    return registry.downloadRepository.listRecent(limit=limit)


@router.post(
    "",
    response_model=DownloadBatchResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def createDownloads(
    payload: DownloadBatchRequest,
    request: Request,
    session: Session = Depends(getSession),
    task_manager: LocalTaskManager = Depends(getTaskManager),
) -> dict:
    registry = createApiRepositoryRegistry(session)
    local_folder = next(
        (
            folder
            for folder in registry.localFolderRepository.list_all()
            if folder.id == payload.local_folder_id
        ),
        None,
    )
    if local_folder is None:
        raise ValueError("La biblioteca de destino no existe.")

    sources = [
        _DownloadSource(source_url=str(source_url))
        for source_url in payload.source_urls
    ]
    requested_item_ids = set(payload.youtube_playlist_item_ids)
    found_item_ids: set[int] = set()
    for playlist in registry.youtubePlaylistRepository.list_all():
        if not requested_item_ids or playlist.id is None:
            continue
        for item in registry.youtubePlaylistItemRepository.list_by_playlist(
            playlist.id
        ):
            if item.id not in requested_item_ids:
                continue
            found_item_ids.add(item.id)
            sources.append(
                _DownloadSource(
                    source_url=(
                        "https://www.youtube.com/watch?v="
                        f"{item.external_video_id}"
                    ),
                    youtube_playlist_item_id=item.id,
                    source_title=item.raw_title,
                    source_artist=item.raw_channel_name,
                )
            )
    missing_item_ids = sorted(requested_item_ids - found_item_ids)
    if missing_item_ids:
        raise ValueError(
            "No existen los items de YouTube solicitados: "
            + ", ".join(str(item_id) for item_id in missing_item_ids)
        )

    session_factory = request.app.state.sessionFactory
    settings = request.app.state.settings
    tasks = [
        task_manager.submit(
            "audio_download",
            _buildDownloadOperation(
                session_factory=session_factory,
                settings=settings,
                local_folder_id=payload.local_folder_id,
                source=source,
            ),
        )
        for source in sources
    ]
    return {"tasks": tasks}


@router.post(
    "/{download_id}/retry",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def retryDownload(
    download_id: int,
    request: Request,
    session: Session = Depends(getSession),
    task_manager: LocalTaskManager = Depends(getTaskManager),
):
    registry = createApiRepositoryRegistry(session)
    download = registry.downloadRepository.getById(download_id)
    if download is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "download_not_found",
            "La descarga solicitada no existe.",
        )
    if download.status not in {"failed", "cancelled"}:
        raise ValueError("Solo se pueden reintentar descargas fallidas o canceladas.")
    source = _DownloadSource(
        source_url=download.source_url,
        youtube_playlist_item_id=download.youtube_playlist_item_id,
        source_title=download.source_title,
        source_artist=download.source_artist,
    )
    return task_manager.submit(
        "audio_download",
        _buildDownloadOperation(
            session_factory=request.app.state.sessionFactory,
            settings=request.app.state.settings,
            local_folder_id=download.local_folder_id,
            source=source,
        ),
    )


def _buildDownloadOperation(
    *,
    session_factory,
    settings=None,
    local_folder_id: int,
    source: _DownloadSource,
):
    resolved_settings = settings or get_settings()

    def operation(context: TaskContext):
        task_session = session_factory()
        registry = createApiRepositoryRegistry(task_session)
        try:
            return DownloadAudioUseCase(
                registry.downloadRepository,
                registry.localFolderRepository,
                registry.localSongRepository,
                YtDlpAudioDownloader(
                    resolved_settings.ffmpeg_path,
                    socket_timeout_seconds=resolved_settings.yt_dlp_timeout_seconds,
                    temporary_folder=str(resolved_settings.temporaryFolderPath),
                ),
                MutagenLocalSongMetadataReader(),
                task_session.commit,
                task_session.rollback,
            ).execute(
                task_id=context.task_id,
                local_folder_id=local_folder_id,
                source_url=source.source_url,
                youtube_playlist_item_id=source.youtube_playlist_item_id,
                source_title=source.source_title,
                source_artist=source.source_artist,
                on_progress=context.reportProgress,
                is_cancelled=lambda: context.isCancelled,
            )
        finally:
            task_session.close()

    return operation
