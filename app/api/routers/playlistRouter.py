from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.apiSchemas import (
    TaskResponse,
    YoutubePlaylistItemResponse,
    YoutubePlaylistRequest,
    YoutubePlaylistResponse,
)
from app.api.dependencies import (
    createApiRepositoryRegistry,
    getSession,
    getTaskManager,
)
from app.application.dto.activateYoutubePlaylistInputDto import (
    ActivateYoutubePlaylistInputDto,
)
from app.application.dto.defineMainYoutubePlaylistInputDto import (
    DefineMainYoutubePlaylistInputDto,
)
from app.application.dto.deleteYoutubePlaylistInputDto import (
    DeleteYoutubePlaylistInputDto,
)
from app.application.dto.updateYoutubePlaylistInputDto import (
    UpdateYoutubePlaylistInputDto,
)
from app.application.use_cases.playlists.activateYoutubePlaylistUseCase import (
    ActivateYoutubePlaylistUseCase,
)
from app.application.use_cases.playlists.defineMainYoutubePlaylistUseCase import (
    DefineMainYoutubePlaylistUseCase,
)
from app.application.use_cases.playlists.deleteYoutubePlaylistUseCase import (
    DeleteYoutubePlaylistUseCase,
)
from app.application.use_cases.playlists.importYoutubePlaylistItemsUseCase import (
    ImportYoutubePlaylistItemsUseCase,
)
from app.application.use_cases.playlists.listYoutubePlaylistsUseCase import (
    ListYoutubePlaylistsUseCase,
)
from app.application.use_cases.playlists.updateYoutubePlaylistUseCase import (
    UpdateYoutubePlaylistUseCase,
)
from app.infrastructure.downloads.youtube import YtDlpYoutubePlaylistItemsImporter
from app.infrastructure.tasks import LocalTaskManager, TaskContext

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=list[YoutubePlaylistResponse])
def listPlaylists(session: Session = Depends(getSession)) -> list:
    registry = createApiRepositoryRegistry(session)
    return ListYoutubePlaylistsUseCase(
        registry.youtubePlaylistRepository,
        registry.youtubePlaylistItemRepository,
    ).execute()


@router.post(
    "",
    response_model=YoutubePlaylistResponse,
    status_code=status.HTTP_201_CREATED,
)
def createPlaylist(
    payload: YoutubePlaylistRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return DefineMainYoutubePlaylistUseCase(
        registry.youtubePlaylistRepository
    ).execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url=str(payload.playlist_url),
            title=payload.title,
        )
    )


@router.put("/{playlist_id}", response_model=YoutubePlaylistResponse)
def updatePlaylist(
    playlist_id: int,
    payload: YoutubePlaylistRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return UpdateYoutubePlaylistUseCase(
        registry.youtubePlaylistRepository
    ).execute(
        UpdateYoutubePlaylistInputDto(
            youtube_playlist_id=playlist_id,
            playlist_url=str(payload.playlist_url),
            title=payload.title,
        )
    )


@router.post("/{playlist_id}/activate", response_model=YoutubePlaylistResponse)
def activatePlaylist(
    playlist_id: int,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return ActivateYoutubePlaylistUseCase(
        registry.youtubePlaylistRepository
    ).execute(
        ActivateYoutubePlaylistInputDto(youtube_playlist_id=playlist_id)
    )


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePlaylist(
    playlist_id: int,
    session: Session = Depends(getSession),
) -> Response:
    registry = createApiRepositoryRegistry(session)
    DeleteYoutubePlaylistUseCase(registry.youtubePlaylistRepository).execute(
        DeleteYoutubePlaylistInputDto(youtube_playlist_id=playlist_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{playlist_id}/items",
    response_model=list[YoutubePlaylistItemResponse],
)
def listPlaylistItems(
    playlist_id: int,
    session: Session = Depends(getSession),
) -> list:
    registry = createApiRepositoryRegistry(session)
    return registry.youtubePlaylistItemRepository.list_by_playlist(playlist_id)


@router.post("/{playlist_id}/import", response_model=TaskResponse)
def importPlaylist(
    playlist_id: int,
    request: Request,
    session: Session = Depends(getSession),
    task_manager: LocalTaskManager = Depends(getTaskManager),
):
    registry = createApiRepositoryRegistry(session)
    ActivateYoutubePlaylistUseCase(
        registry.youtubePlaylistRepository
    ).execute(
        ActivateYoutubePlaylistInputDto(youtube_playlist_id=playlist_id)
    )
    session_factory = request.app.state.sessionFactory

    def operation(context: TaskContext):
        context.reportProgress(1.0, "Consultando la playlist en YouTube…")
        task_session = session_factory()
        task_registry = createApiRepositoryRegistry(task_session)
        try:
            result = ImportYoutubePlaylistItemsUseCase(
                task_registry.youtubePlaylistRepository,
                task_registry.youtubePlaylistItemRepository,
                YtDlpYoutubePlaylistItemsImporter(),
            ).execute()
            context.reportProgress(100.0, "Playlist importada.")
            return result
        except Exception:
            task_session.rollback()
            raise
        finally:
            task_session.close()

    return task_manager.submit("playlist_import", operation)
