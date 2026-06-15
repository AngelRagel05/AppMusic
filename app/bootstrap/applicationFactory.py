from __future__ import annotations

from app.application.use_cases import (
    ActivateLocalFolderUseCase,
    ActivateYoutubePlaylistUseCase,
    CompareYoutubePlaylistWithLocalLibraryUseCase,
    CreateIgnoredTermUseCase,
    DeleteIgnoredTermUseCase,
    DeleteLocalFolderUseCase,
    DeleteYoutubePlaylistUseCase,
    DefineMainLocalFolderUseCase,
    DefineMainYoutubePlaylistUseCase,
    GetActiveLocalFolderUseCase,
    GetActiveYoutubePlaylistUseCase,
    ImportYoutubePlaylistItemsUseCase,
    ListPersistedPlaylistComparisonHistoryUseCase,
    ListActiveLocalSongsUseCase,
    ListIgnoredTermsUseCase,
    ListLocalFoldersUseCase,
    LoadPersistedPlaylistComparisonUseCase,
    ListYoutubePlaylistsUseCase,
    ScanLocalFolderUseCase,
    UpdatePlaylistComparisonResultUseCase,
    UpdateIgnoredTermUseCase,
    UpdateLocalFolderUseCase,
    UpdateYoutubePlaylistUseCase,
)
from app.bootstrap.persistenceFactory import PersistenceFactory
from app.bootstrap.presentationFactory import DesktopApplication, PresentationFactory
from app.bootstrap.serviceRegistry import ServiceRegistry
from app.infrastructure.filesystem import LocalMusicScanner
from app.infrastructure.downloads.youtube import YtDlpYoutubePlaylistItemsImporter
from app.infrastructure.metadata import MutagenLocalSongMetadataReader
from app.presentation.viewmodels import (
    IgnoredTermsViewModel,
    LibraryComparisonViewModel,
    LocalFolderViewModel,
    LocalLibraryScanViewModel,
    YoutubePlaylistImportViewModel,
    YoutubePlaylistViewModel,
)


class ApplicationFactory:
    def __init__(
        self,
        persistence_factory: PersistenceFactory | None = None,
        presentation_factory: PresentationFactory | None = None,
    ) -> None:
        self._persistence_factory = persistence_factory or PersistenceFactory()
        self._presentation_factory = presentation_factory or PresentationFactory()

    def bootstrapDatabase(self) -> None:
        self._persistence_factory.bootstrapDatabase()

    def createServiceRegistry(self) -> ServiceRegistry:
        persistence_registry = self._persistence_factory.createRegistry()
        localLibraryScanViewModel = LocalLibraryScanViewModel(
            self._executeScanLocalFolderInBackground
        )

        ignoredTermsViewModel = IgnoredTermsViewModel(
            list_use_case=ListIgnoredTermsUseCase(
                persistence_registry.ignoredTermRepository
            ),
            create_use_case=CreateIgnoredTermUseCase(
                persistence_registry.ignoredTermRepository
            ),
            update_use_case=UpdateIgnoredTermUseCase(
                persistence_registry.ignoredTermRepository
            ),
            delete_use_case=DeleteIgnoredTermUseCase(
                persistence_registry.ignoredTermRepository
            ),
        )
        localFolderViewModel = LocalFolderViewModel(
            list_use_case=ListLocalFoldersUseCase(
                persistence_registry.localFolderRepository
            ),
            get_active_use_case=GetActiveLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            activate_use_case=ActivateLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            define_main_use_case=DefineMainLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            update_use_case=UpdateLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            delete_use_case=DeleteLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
        )
        youtubePlaylistViewModel = YoutubePlaylistViewModel(
            list_use_case=ListYoutubePlaylistsUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.youtubePlaylistItemRepository,
            ),
            get_active_use_case=GetActiveYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.youtubePlaylistItemRepository,
            ),
            activate_use_case=ActivateYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            define_main_use_case=DefineMainYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            update_use_case=UpdateYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            delete_use_case=DeleteYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
        )
        youtubePlaylistImportViewModel = YoutubePlaylistImportViewModel(
            self._executeImportYoutubePlaylistItemsInBackground
        )
        libraryComparisonViewModel = LibraryComparisonViewModel(
            self._loadLibraryComparisonInBackground,
            self._loadPersistedLibraryComparison,
            self._updatePersistedComparisonResult,
        )

        return ServiceRegistry(
            session=persistence_registry.session,
            ignoredTermsViewModel=ignoredTermsViewModel,
            libraryComparisonViewModel=libraryComparisonViewModel,
            localFolderViewModel=localFolderViewModel,
            localLibraryScanViewModel=localLibraryScanViewModel,
            youtubePlaylistImportViewModel=youtubePlaylistImportViewModel,
            youtubePlaylistViewModel=youtubePlaylistViewModel,
        )

    def createDesktopApplication(self, appName: str) -> DesktopApplication:
        service_registry = self.createServiceRegistry()
        return self._presentation_factory.createDesktopApplication(
            app_name=appName,
            service_registry=service_registry,
        )

    def _executeScanLocalFolderInBackground(self, on_progress) -> object:
        persistence_registry = self._persistence_factory.createRegistry()
        try:
            scan_local_folder_use_case = ScanLocalFolderUseCase(
                persistence_registry.localFolderRepository,
                persistence_registry.localSongRepository,
                LocalMusicScanner(),
                MutagenLocalSongMetadataReader(),
            )
            return scan_local_folder_use_case.execute(on_progress=on_progress)
        finally:
            persistence_registry.session.close()

    def _executeImportYoutubePlaylistItemsInBackground(self):
        persistence_registry = self._persistence_factory.createRegistry()
        try:
            import_youtube_playlist_items_use_case = ImportYoutubePlaylistItemsUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.youtubePlaylistItemRepository,
                YtDlpYoutubePlaylistItemsImporter(),
            )
            return import_youtube_playlist_items_use_case.execute()
        finally:
            persistence_registry.session.close()

    def _loadLibraryComparisonInBackground(self):
        persistence_registry = self._persistence_factory.createRegistry()
        try:
            local_songs = ListActiveLocalSongsUseCase(
                persistence_registry.localFolderRepository,
                persistence_registry.localSongRepository,
            ).execute()
            comparison_result = CompareYoutubePlaylistWithLocalLibraryUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.youtubePlaylistItemRepository,
                persistence_registry.localFolderRepository,
                persistence_registry.localSongRepository,
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
                persistence_registry.ignoredTermRepository,
            ).execute()
            comparison_history = ListPersistedPlaylistComparisonHistoryUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.localFolderRepository,
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
            ).execute()
            return local_songs, comparison_result, comparison_history
        finally:
            persistence_registry.session.close()

    def _loadPersistedLibraryComparison(self):
        persistence_registry = self._persistence_factory.createRegistry()
        try:
            persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.youtubePlaylistItemRepository,
                persistence_registry.localFolderRepository,
                persistence_registry.localSongRepository,
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
            ).execute()
            if persisted_snapshot is None:
                return None
            local_songs, comparison_result = persisted_snapshot
            comparison_history = ListPersistedPlaylistComparisonHistoryUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.localFolderRepository,
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
            ).execute()
            return local_songs, comparison_result, comparison_history
        finally:
            persistence_registry.session.close()

    def _updatePersistedComparisonResult(self, input_dto):
        persistence_registry = self._persistence_factory.createRegistry()
        try:
            UpdatePlaylistComparisonResultUseCase(
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
                persistence_registry.localSongRepository,
            ).execute(input_dto)
            persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.youtubePlaylistItemRepository,
                persistence_registry.localFolderRepository,
                persistence_registry.localSongRepository,
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
            ).execute()
            if persisted_snapshot is None:
                return None
            local_songs, comparison_result = persisted_snapshot
            comparison_history = ListPersistedPlaylistComparisonHistoryUseCase(
                persistence_registry.youtubePlaylistRepository,
                persistence_registry.localFolderRepository,
                persistence_registry.playlistComparisonRepository,
                persistence_registry.playlistComparisonResultRepository,
            ).execute()
            return local_songs, comparison_result, comparison_history
        finally:
            persistence_registry.session.close()
