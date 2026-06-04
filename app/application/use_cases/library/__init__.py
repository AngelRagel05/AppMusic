"""Library use cases."""

from app.application.use_cases.library.activateLocalFolderUseCase import (
    ActivateLocalFolderUseCase,
)
from app.application.use_cases.library.defineMainLocalFolderUseCase import (
    DefineMainLocalFolderUseCase,
)
from app.application.use_cases.library.deleteLocalFolderUseCase import (
    DeleteLocalFolderUseCase,
)
from app.application.use_cases.library.getActiveLocalFolderUseCase import (
    GetActiveLocalFolderUseCase,
)
from app.application.use_cases.library.listActiveLocalSongsUseCase import (
    ListActiveLocalSongsUseCase,
)
from app.application.use_cases.library.listLocalFoldersUseCase import (
    ListLocalFoldersUseCase,
)
from app.application.use_cases.library.updateLocalFolderUseCase import (
    UpdateLocalFolderUseCase,
)

__all__ = [
    "ActivateLocalFolderUseCase",
    "DefineMainLocalFolderUseCase",
    "DeleteLocalFolderUseCase",
    "GetActiveLocalFolderUseCase",
    "ListActiveLocalSongsUseCase",
    "ListLocalFoldersUseCase",
    "UpdateLocalFolderUseCase",
]
