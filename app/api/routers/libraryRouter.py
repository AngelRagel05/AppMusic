from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.apiSchemas import LocalFolderRequest, LocalFolderResponse, TaskResponse
from app.api.dependencies import (
    createApiRepositoryRegistry,
    getSession,
    getTaskManager,
)
from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.dto.deleteLocalFolderInputDto import DeleteLocalFolderInputDto
from app.application.dto.updateLocalFolderInputDto import UpdateLocalFolderInputDto
from app.application.use_cases.library.activateLocalFolderUseCase import (
    ActivateLocalFolderUseCase,
)
from app.application.use_cases.library.defineMainLocalFolderUseCase import (
    DefineMainLocalFolderUseCase,
)
from app.application.use_cases.library.deleteLocalFolderUseCase import (
    DeleteLocalFolderUseCase,
)
from app.application.use_cases.library.listLocalFoldersUseCase import (
    ListLocalFoldersUseCase,
)
from app.application.use_cases.library.scanLocalFolderUseCase import (
    ScanLocalFolderUseCase,
)
from app.application.use_cases.library.updateLocalFolderUseCase import (
    UpdateLocalFolderUseCase,
)
from app.infrastructure.filesystem import LocalMusicScanner
from app.infrastructure.metadata import MutagenLocalSongMetadataReader
from app.infrastructure.tasks import LocalTaskManager, TaskContext

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=list[LocalFolderResponse])
def listLibraries(session: Session = Depends(getSession)) -> list:
    registry = createApiRepositoryRegistry(session)
    return ListLocalFoldersUseCase(registry.localFolderRepository).execute()


@router.post(
    "",
    response_model=LocalFolderResponse,
    status_code=status.HTTP_201_CREATED,
)
def createLibrary(
    payload: LocalFolderRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return DefineMainLocalFolderUseCase(registry.localFolderRepository).execute(
        DefineMainLocalFolderInputDto(
            path=payload.path,
            display_name=payload.display_name,
        )
    )


@router.put("/{library_id}", response_model=LocalFolderResponse)
def updateLibrary(
    library_id: int,
    payload: LocalFolderRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return UpdateLocalFolderUseCase(registry.localFolderRepository).execute(
        UpdateLocalFolderInputDto(
            local_folder_id=library_id,
            path=payload.path,
            display_name=payload.display_name,
        )
    )


@router.post("/{library_id}/activate", response_model=LocalFolderResponse)
def activateLibrary(
    library_id: int,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return ActivateLocalFolderUseCase(registry.localFolderRepository).execute(
        ActivateLocalFolderInputDto(local_folder_id=library_id)
    )


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def deleteLibrary(
    library_id: int,
    session: Session = Depends(getSession),
) -> Response:
    registry = createApiRepositoryRegistry(session)
    DeleteLocalFolderUseCase(registry.localFolderRepository).execute(
        DeleteLocalFolderInputDto(local_folder_id=library_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{library_id}/scan", response_model=TaskResponse)
def scanLibrary(
    library_id: int,
    request: Request,
    session: Session = Depends(getSession),
    task_manager: LocalTaskManager = Depends(getTaskManager),
):
    registry = createApiRepositoryRegistry(session)
    ActivateLocalFolderUseCase(registry.localFolderRepository).execute(
        ActivateLocalFolderInputDto(local_folder_id=library_id)
    )
    session_factory = request.app.state.sessionFactory

    def operation(context: TaskContext):
        task_session = session_factory()
        task_registry = createApiRepositoryRegistry(task_session)
        try:
            use_case = ScanLocalFolderUseCase(
                task_registry.localFolderRepository,
                task_registry.localSongRepository,
                LocalMusicScanner(),
                MutagenLocalSongMetadataReader(),
            )

            def reportProgress(progress) -> None:
                total = progress.total_song_count
                percent = (
                    progress.processed_song_count * 100.0 / total
                    if total
                    else 100.0
                )
                context.reportProgress(
                    percent,
                    (
                        f"Escaneadas {progress.processed_song_count} "
                        f"de {total} canciones."
                    ),
                )

            result = use_case.execute(
                on_progress=reportProgress,
                is_cancelled=lambda: context.isCancelled,
            )
            task_session.commit()
            return result
        except Exception:
            task_session.rollback()
            raise
        finally:
            task_session.close()

    return task_manager.submit("library_scan", operation)
