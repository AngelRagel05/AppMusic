from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.apiSchemas import (
    LocalSongMetadataRequest,
    LocalSongPageResponse,
    LocalSongResponse,
)
from app.api.dependencies import createApiRepositoryRegistry, getSession
from app.application.dto.localSongMetadataUpdateDto import (
    LocalSongMetadataUpdateDto,
)
from app.application.use_cases.metadata import (
    GetLocalSongUseCase,
    ListLocalSongsUseCase,
    RefreshLocalSongMetadataUseCase,
    UpdateLocalSongMetadataUseCase,
)
from app.infrastructure.metadata import (
    MutagenLocalSongMetadataReader,
    MutagenLocalSongMetadataWriter,
)

router = APIRouter(prefix="/songs", tags=["metadata"])


@router.get("", response_model=LocalSongPageResponse)
def listSongs(
    request: Request,
    library_id: int | None = Query(default=None, alias="libraryId"),
    search: str = Query(default="", max_length=255),
    availability: str = Query(default="all"),
    sort_by: str = Query(default="title", alias="sortBy"),
    sort_direction: str = Query(default="asc", alias="sortDirection"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, alias="pageSize"),
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    resolved_library_id = _resolveLibraryId(registry, library_id)
    return ListLocalSongsUseCase(registry.localSongRepository).execute(
        local_folder_id=resolved_library_id,
        search=search,
        availability=availability,
        sort_by=sort_by,
        sort_direction=sort_direction,
        page=page,
        page_size=min(page_size, request.app.state.settings.max_page_size),
    )


@router.get("/{song_id}", response_model=LocalSongResponse)
def getSong(
    song_id: int,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return GetLocalSongUseCase(registry.localSongRepository).execute(song_id)


@router.put("/{song_id}/metadata", response_model=LocalSongResponse)
def updateSongMetadata(
    song_id: int,
    payload: LocalSongMetadataRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    result = UpdateLocalSongMetadataUseCase(
        registry.localSongRepository,
        registry.localFolderRepository,
        MutagenLocalSongMetadataWriter(),
        MutagenLocalSongMetadataReader(),
    ).execute(
        song_id,
        LocalSongMetadataUpdateDto(
            title=payload.title,
            artist=payload.artist,
            album=payload.album,
            release_year=payload.release_year,
            track_number_album=payload.track_number_album,
        ),
    )
    session.commit()
    return result


@router.post("/{song_id}/refresh", response_model=LocalSongResponse)
def refreshSongMetadata(
    song_id: int,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    result = RefreshLocalSongMetadataUseCase(
        registry.localSongRepository,
        registry.localFolderRepository,
        MutagenLocalSongMetadataReader(),
    ).execute(song_id)
    session.commit()
    return result


def _resolveLibraryId(registry, library_id: int | None) -> int:
    if library_id is not None:
        return library_id
    active_folder = registry.localFolderRepository.get_active()
    if active_folder is None or active_folder.id is None:
        raise ValueError("No hay una biblioteca local activa.")
    return active_folder.id
