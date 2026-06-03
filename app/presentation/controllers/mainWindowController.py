from __future__ import annotations

from app.presentation.controllers.ignoredTermsController import IgnoredTermsController
from app.presentation.controllers.localLibrariesController import LocalLibrariesController
from app.presentation.controllers.youtubePlaylistsController import (
    YoutubePlaylistsController,
)
from app.presentation.ui.mainScreen.mainWindow.mainWindow import MainWindow
from app.presentation.viewmodels.ignoredTermsViewModel import IgnoredTermsViewModel
from app.presentation.viewmodels.localFolderViewModel import LocalFolderViewModel
from app.presentation.viewmodels.youtubePlaylistViewModel import YoutubePlaylistViewModel


class MainWindowController:
    def __init__(
        self,
        view: MainWindow,
        local_folder_view_model: LocalFolderViewModel,
        youtube_playlist_view_model: YoutubePlaylistViewModel,
        ignored_terms_view_model: IgnoredTermsViewModel,
    ) -> None:
        self._view = view
        self._last_action_message = "Todavia no hay acciones registradas"
        self._local_libraries_controller = LocalLibrariesController(
            view=view,
            view_model=local_folder_view_model,
            on_state_changed=self._updateSyncStatus,
            on_action_recorded=self._recordLastAction,
        )
        self._youtube_playlists_controller = YoutubePlaylistsController(
            view=view,
            view_model=youtube_playlist_view_model,
            on_state_changed=self._updateSyncStatus,
            on_action_recorded=self._recordLastAction,
        )
        self._ignored_terms_controller = IgnoredTermsController(
            view=view,
            view_model=ignored_terms_view_model,
            on_action_recorded=self._recordLastAction,
        )

    def initialize(self) -> None:
        self._local_libraries_controller.bindEvents()
        self._youtube_playlists_controller.bindEvents()
        self._ignored_terms_controller.bindEvents()

        self._local_libraries_controller.load()
        self._youtube_playlists_controller.load()
        self._ignored_terms_controller.load()
        self._view.page.setLastAction(self._last_action_message)

    def _updateSyncStatus(self) -> None:
        active_folder = self._local_libraries_controller.activeFolder()
        active_playlist = self._youtube_playlists_controller.activePlaylist()
        if active_folder is not None and active_playlist is not None:
            self._view.page.setSyncStatus("Listo", state="ready")
            return

        self._view.page.setSyncStatus("Pendiente", state="idle")

    def _recordLastAction(self, message: str) -> None:
        self._last_action_message = message
        self._view.page.setLastAction(message)
