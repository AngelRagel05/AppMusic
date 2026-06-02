"""Application use cases."""

from app.application.use_cases.activateLocalFolderUseCase import ActivateLocalFolderUseCase
from app.application.use_cases.activateYoutubePlaylistUseCase import (
    ActivateYoutubePlaylistUseCase,
)
from app.application.use_cases.bootstrap_database_use_case import BootstrapDatabaseUseCase
from app.application.use_cases.create_ignored_term_use_case import CreateIgnoredTermUseCase
from app.application.use_cases.deleteLocalFolderUseCase import DeleteLocalFolderUseCase
from app.application.use_cases.deleteYoutubePlaylistUseCase import (
    DeleteYoutubePlaylistUseCase,
)
from app.application.use_cases.defineMainLocalFolderUseCase import (
    DefineMainLocalFolderUseCase,
)
from app.application.use_cases.defineMainYoutubePlaylistUseCase import (
    DefineMainYoutubePlaylistUseCase,
)
from app.application.use_cases.getActiveLocalFolderUseCase import (
    GetActiveLocalFolderUseCase,
)
from app.application.use_cases.getActiveYoutubePlaylistUseCase import (
    GetActiveYoutubePlaylistUseCase,
)
from app.application.use_cases.listLocalFoldersUseCase import ListLocalFoldersUseCase
from app.application.use_cases.listYoutubePlaylistsUseCase import (
    ListYoutubePlaylistsUseCase,
)
from app.application.use_cases.list_ignored_terms_use_case import ListIgnoredTermsUseCase
from app.application.use_cases.updateLocalFolderUseCase import UpdateLocalFolderUseCase
from app.application.use_cases.updateYoutubePlaylistUseCase import (
    UpdateYoutubePlaylistUseCase,
)

__all__ = [
    "ActivateLocalFolderUseCase",
    "ActivateYoutubePlaylistUseCase",
    "BootstrapDatabaseUseCase",
    "CreateIgnoredTermUseCase",
    "DeleteLocalFolderUseCase",
    "DeleteYoutubePlaylistUseCase",
    "DefineMainLocalFolderUseCase",
    "DefineMainYoutubePlaylistUseCase",
    "GetActiveLocalFolderUseCase",
    "GetActiveYoutubePlaylistUseCase",
    "ListLocalFoldersUseCase",
    "ListYoutubePlaylistsUseCase",
    "ListIgnoredTermsUseCase",
    "UpdateLocalFolderUseCase",
    "UpdateYoutubePlaylistUseCase",
]
