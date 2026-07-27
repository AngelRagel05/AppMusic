from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.apiSchemas import (
    ComparisonHistoryResponse,
    ComparisonItemResponse,
    ComparisonResponse,
    ComparisonUpdateRequest,
    TaskResponse,
)
from app.api.dependencies import (
    createApiRepositoryRegistry,
    getSession,
    getTaskManager,
)
from app.api.errors import ApiError
from app.application.dto.updatePlaylistComparisonResultInputDto import (
    UpdatePlaylistComparisonResultInputDto,
)
from app.application.use_cases.playlists.compareYoutubePlaylistWithLocalLibraryUseCase import (
    CompareYoutubePlaylistWithLocalLibraryUseCase,
)
from app.application.use_cases.playlists.listPersistedPlaylistComparisonHistoryUseCase import (
    ListPersistedPlaylistComparisonHistoryUseCase,
)
from app.application.use_cases.playlists.loadPersistedPlaylistComparisonUseCase import (
    LoadPersistedPlaylistComparisonUseCase,
)
from app.application.use_cases.playlists.updatePlaylistComparisonResultUseCase import (
    UpdatePlaylistComparisonResultUseCase,
)
from app.infrastructure.tasks import LocalTaskManager, TaskContext

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.get("/current", response_model=ComparisonResponse)
def getCurrentComparison(
    request: Request,
    search: str = Query(default="", max_length=255),
    match_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, alias="pageSize"),
    session: Session = Depends(getSession),
):
    return _loadComparison(
        session=session,
        comparison_id=None,
        search=search,
        match_status=match_status,
        page=page,
        page_size=min(page_size, request.app.state.settings.max_page_size),
    )


@router.get("/history", response_model=list[ComparisonHistoryResponse])
def listComparisonHistory(
    request: Request,
    session: Session = Depends(getSession),
) -> list:
    registry = createApiRepositoryRegistry(session)
    return ListPersistedPlaylistComparisonHistoryUseCase(
        registry.youtubePlaylistRepository,
        registry.localFolderRepository,
        registry.playlistComparisonRepository,
        registry.playlistComparisonResultRepository,
    ).execute(limit=request.app.state.settings.comparison_history_limit)


@router.get("/{comparison_id}", response_model=ComparisonResponse)
def getComparison(
    comparison_id: int,
    request: Request,
    search: str = Query(default="", max_length=255),
    match_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, alias="pageSize"),
    session: Session = Depends(getSession),
):
    return _loadComparison(
        session=session,
        comparison_id=comparison_id,
        search=search,
        match_status=match_status,
        page=page,
        page_size=min(page_size, request.app.state.settings.max_page_size),
    )


@router.post("/run", response_model=TaskResponse)
def runComparison(
    request: Request,
    force_full_recompute: bool = Query(default=False, alias="forceFullRecompute"),
    task_manager: LocalTaskManager = Depends(getTaskManager),
):
    session_factory = request.app.state.sessionFactory

    def operation(context: TaskContext):
        context.reportProgress(5.0, "Preparando snapshots de comparacion…")
        task_session = session_factory()
        registry = createApiRepositoryRegistry(task_session)
        try:
            result = CompareYoutubePlaylistWithLocalLibraryUseCase(
                registry.youtubePlaylistRepository,
                registry.youtubePlaylistItemRepository,
                registry.localFolderRepository,
                registry.localSongRepository,
                registry.playlistComparisonRepository,
                registry.playlistComparisonResultRepository,
                registry.ignoredTermRepository,
            ).execute(force_full_recompute=force_full_recompute)
            context.reportProgress(100.0, "Comparacion completada.")
            return result
        except Exception:
            task_session.rollback()
            raise
        finally:
            task_session.close()

    return task_manager.submit("library_comparison", operation)


@router.patch(
    "/{comparison_id}/items/{youtube_item_id}",
    response_model=ComparisonItemResponse,
)
def updateComparisonItem(
    comparison_id: int,
    youtube_item_id: int,
    payload: ComparisonUpdateRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    UpdatePlaylistComparisonResultUseCase(
        registry.playlistComparisonRepository,
        registry.playlistComparisonResultRepository,
        registry.localSongRepository,
    ).execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=comparison_id,
            youtube_playlist_item_id=youtube_item_id,
            match_status=payload.match_status,
            local_song_id=payload.local_song_id,
        )
    )
    snapshot = LoadPersistedPlaylistComparisonUseCase(
        registry.youtubePlaylistRepository,
        registry.youtubePlaylistItemRepository,
        registry.localFolderRepository,
        registry.localSongRepository,
        registry.playlistComparisonRepository,
        registry.playlistComparisonResultRepository,
    ).execute(playlist_comparison_id=comparison_id)
    if snapshot is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "comparison_not_found",
            "La comparacion actualizada ya no esta disponible.",
        )
    _local_songs, comparison = snapshot
    item = next(
        (
            candidate
            for candidate in comparison.items
            if candidate.youtube_playlist_item_id == youtube_item_id
        ),
        None,
    )
    if item is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "comparison_item_not_found",
            "El resultado actualizado ya no esta disponible.",
        )
    return item


def _loadComparison(
    *,
    session: Session,
    comparison_id: int | None,
    search: str,
    match_status: str | None,
    page: int,
    page_size: int,
) -> dict:
    if match_status not in {None, "found", "missing", "possible_match"}:
        raise ValueError("El estado de comparacion solicitado no es valido.")
    registry = createApiRepositoryRegistry(session)
    snapshot = LoadPersistedPlaylistComparisonUseCase(
        registry.youtubePlaylistRepository,
        registry.youtubePlaylistItemRepository,
        registry.localFolderRepository,
        registry.localSongRepository,
        registry.playlistComparisonRepository,
        registry.playlistComparisonResultRepository,
    ).execute(playlist_comparison_id=comparison_id)
    if snapshot is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "comparison_not_found",
            "Todavia no existe una comparacion para el contexto activo.",
        )
    _local_songs, comparison = snapshot
    normalized_search = search.strip().casefold()
    filtered_items = [
        item
        for item in comparison.items
        if (
            match_status is None
            or item.comparison_status.value == match_status
        )
        and (
            not normalized_search
            or normalized_search in item.youtube_title.casefold()
            or normalized_search in item.youtube_artist.casefold()
            or normalized_search in (item.local_title or "").casefold()
            or normalized_search in (item.local_artist or "").casefold()
        )
    ]
    start = (page - 1) * page_size
    return {
        "summary": comparison.summary,
        "items": filtered_items[start : start + page_size],
        "playlist_comparison_id": comparison.playlist_comparison_id,
        "last_compared_at": comparison.last_compared_at,
        "total": len(filtered_items),
        "page": page,
        "page_size": page_size,
    }
