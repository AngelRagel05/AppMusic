from __future__ import annotations

from app.presentation.features.ignoredTerms.controller import IgnoredTermsController
from app.presentation.features.localLibrary.controller import LocalLibraryController
from app.presentation.features.youtubePlaylists.controller import (
    YoutubePlaylistsController,
)
from app.presentation.viewmodels import (
    IgnoredTermsViewModel,
    LocalFolderViewModel,
    YoutubePlaylistViewModel,
)
from app.presentation.windows.mainWindow.mainWindow import MainWindow


class AppShellController:
    def __init__(
        self,
        view: MainWindow,
        local_folder_view_model: LocalFolderViewModel,
        youtube_playlist_view_model: YoutubePlaylistViewModel,
        ignored_terms_view_model: IgnoredTermsViewModel,
    ) -> None:
        self._view = view
        self._last_action_message = "Todavia no hay acciones registradas"
        self._local_library_controller = LocalLibraryController(
            page=view.page.localLibraryPage,
            view_model=local_folder_view_model,
            show_page=view.page.showPage,
            on_state_changed=self._updateSyncStatus,
            on_action_recorded=self._recordLastAction,
            on_active_folder_changed=self._view.page.setActiveFolderName,
            on_song_count_changed=self._view.page.setSongCount,
        )
        self._youtube_playlists_controller = YoutubePlaylistsController(
            page=view.page.youtubePlaylistsPage,
            view_model=youtube_playlist_view_model,
            show_page=view.page.showPage,
            on_state_changed=self._updateSyncStatus,
            on_action_recorded=self._recordLastAction,
            on_active_playlist_changed=self._view.page.setActivePlaylistTitle,
        )
        self._ignored_terms_controller = IgnoredTermsController(
            page=view.page.ignoredTermsPage,
            view_model=ignored_terms_view_model,
            show_page=view.page.showPage,
            on_action_recorded=self._recordLastAction,
        )

    def initialize(self) -> None:
        self._local_library_controller.bindEvents()
        self._youtube_playlists_controller.bindEvents()
        self._ignored_terms_controller.bindEvents()

        self._local_library_controller.load()
        self._youtube_playlists_controller.load()
        self._ignored_terms_controller.load()
        self._view.page.setLastAction(self._last_action_message)

    def _updateSyncStatus(self) -> None:
        active_folder = self._local_library_controller.activeFolder()
        active_playlist = self._youtube_playlists_controller.activePlaylist()
        if active_folder is not None and active_playlist is not None:
            self._view.page.setSyncStatus("Listo", state="ready")
            return

        self._view.page.setSyncStatus("Pendiente", state="idle")

    def _recordLastAction(self, message: str) -> None:
        self._last_action_message = message
        self._view.page.setLastAction(message)
