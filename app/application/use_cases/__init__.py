"""Application use cases."""

from app.application.use_cases.filters.createIgnoredTermUseCase import (
    CreateIgnoredTermUseCase,
)
from app.application.use_cases.filters.deleteIgnoredTermUseCase import (
    DeleteIgnoredTermUseCase,
)
from app.application.use_cases.filters.listIgnoredTermsUseCase import (
    ListIgnoredTermsUseCase,
)
from app.application.use_cases.filters.updateIgnoredTermUseCase import (
    UpdateIgnoredTermUseCase,
)
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
from app.application.use_cases.library.listLocalFoldersUseCase import (
    ListLocalFoldersUseCase,
)
from app.application.use_cases.library.scanLocalFolderUseCase import (
    ScanLocalFolderUseCase,
)
from app.application.use_cases.library.updateLocalFolderUseCase import (
    UpdateLocalFolderUseCase,
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
from app.application.use_cases.playlists.getActiveYoutubePlaylistUseCase import (
    GetActiveYoutubePlaylistUseCase,
)
from app.application.use_cases.playlists.listActiveYoutubePlaylistItemsUseCase import (
    ListActiveYoutubePlaylistItemsUseCase,
)
from app.application.use_cases.playlists.importYoutubePlaylistItemsUseCase import (
    ImportYoutubePlaylistItemsUseCase,
)
from app.application.use_cases.playlists.listYoutubePlaylistsUseCase import (
    ListYoutubePlaylistsUseCase,
)
from app.application.use_cases.playlists.compareYoutubePlaylistWithLocalLibraryUseCase import (
    CompareYoutubePlaylistWithLocalLibraryUseCase,
)
from app.application.use_cases.playlists.updateYoutubePlaylistUseCase import (
    UpdateYoutubePlaylistUseCase,
)
from app.application.use_cases.system.bootstrapDatabaseUseCase import (
    BootstrapDatabaseUseCase,
)

__all__ = [
    "ActivateLocalFolderUseCase",
    "ActivateYoutubePlaylistUseCase",
    "BootstrapDatabaseUseCase",
    "CreateIgnoredTermUseCase",
    "DeleteIgnoredTermUseCase",
    "DeleteLocalFolderUseCase",
    "DeleteYoutubePlaylistUseCase",
    "DefineMainLocalFolderUseCase",
    "DefineMainYoutubePlaylistUseCase",
    "GetActiveLocalFolderUseCase",
    "GetActiveYoutubePlaylistUseCase",
    "ListActiveYoutubePlaylistItemsUseCase",
    "ImportYoutubePlaylistItemsUseCase",
    "ListLocalFoldersUseCase",
    "ListYoutubePlaylistsUseCase",
    "CompareYoutubePlaylistWithLocalLibraryUseCase",
    "ListIgnoredTermsUseCase",
    "ScanLocalFolderUseCase",
    "UpdateLocalFolderUseCase",
    "UpdateIgnoredTermUseCase",
    "UpdateYoutubePlaylistUseCase",
]
