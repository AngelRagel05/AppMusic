"""Application use cases."""

from app.application.use_cases.activateLocalFolderUseCase import ActivateLocalFolderUseCase
from app.application.use_cases.activateYoutubePlaylistUseCase import (
    ActivateYoutubePlaylistUseCase,
)
from app.application.use_cases.bootstrap_database_use_case import BootstrapDatabaseUseCase
from app.application.use_cases.create_ignored_term_use_case import CreateIgnoredTermUseCase
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

__all__ = [
    "ActivateLocalFolderUseCase",
    "ActivateYoutubePlaylistUseCase",
    "BootstrapDatabaseUseCase",
    "CreateIgnoredTermUseCase",
    "DefineMainLocalFolderUseCase",
    "DefineMainYoutubePlaylistUseCase",
    "GetActiveLocalFolderUseCase",
    "GetActiveYoutubePlaylistUseCase",
    "ListLocalFoldersUseCase",
    "ListYoutubePlaylistsUseCase",
    "ListIgnoredTermsUseCase",
]
