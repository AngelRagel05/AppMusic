from __future__ import annotations

from PySide6.QtWidgets import QFileDialog

from app.presentation.ui.mainScreen.mainWindow.mainWindow import MainWindow
from app.presentation.viewmodels.ignored_terms_view_model import IgnoredTermsViewModel
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
        self._local_folder_view_model = local_folder_view_model
        self._youtube_playlist_view_model = youtube_playlist_view_model
        self._ignored_terms_view_model = ignored_terms_view_model

    def initialize(self) -> None:
        page = self._view.page
        page.localLibrariesSection.browseFolderButton.clicked.connect(self._handle_browse_folder)
        page.localLibrariesSection.saveFolderButton.clicked.connect(self._handle_save_folder)
        page.localLibrariesSection.activateFolderButton.clicked.connect(
            self._handle_activate_folder
        )
        page.youtubePlaylistsSection.savePlaylistButton.clicked.connect(
            self._handle_save_playlist
        )
        page.youtubePlaylistsSection.activatePlaylistButton.clicked.connect(
            self._handle_activate_playlist
        )
        page.ignoredTermsSection.createButton.clicked.connect(self._handle_create_term)

        self._load_folders()
        self._load_playlists()
        self._load_terms()

    def _load_folders(self) -> None:
        local_folders = self._local_folder_view_model.load_folders()
        active_folder = self._local_folder_view_model.load_active_folder()
        self._view.page.localLibrariesSection.showFolders(local_folders)
        self._view.page.localLibrariesSection.showActiveFolder(active_folder)
        self._view.page.heroSection.showLibraryCount(len(local_folders))
        self._view.page.heroSection.showActiveFolderName(
            active_folder.display_name if active_folder is not None else "Sin biblioteca activa"
        )

    def _load_playlists(self) -> None:
        youtube_playlists = self._youtube_playlist_view_model.load_playlists()
        active_playlist = self._youtube_playlist_view_model.load_active_playlist()
        self._view.page.youtubePlaylistsSection.showPlaylists(youtube_playlists)
        self._view.page.youtubePlaylistsSection.showActivePlaylist(active_playlist)
        self._view.page.heroSection.showPlaylistCount(len(youtube_playlists))
        self._view.page.heroSection.showActivePlaylistTitle(
            active_playlist.title if active_playlist is not None else "Sin playlist activa"
        )

    def _load_terms(self) -> None:
        ignored_terms = self._ignored_terms_view_model.load_terms()
        self._view.page.ignoredTermsSection.showTerms(ignored_terms)

    def _handle_browse_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self._view,
            "Seleccionar carpeta principal",
            self._view.page.localLibrariesSection.folderPath(),
        )
        if selected_folder:
            self._view.page.localLibrariesSection.setFolderPath(selected_folder)

    def _handle_save_folder(self) -> None:
        try:
            local_folder = self._local_folder_view_model.define_main_folder(
                self._view.page.localLibrariesSection.folderPath()
            )
        except ValueError as exc:
            self._view.page.heroSection.showStatusMessage(str(exc))
            return

        self._load_folders()
        self._view.page.heroSection.showStatusMessage(
            f'Biblioteca "{local_folder.display_name}" guardada y activada correctamente.'
        )

    def _handle_activate_folder(self) -> None:
        selected_folder_id = self._view.page.localLibrariesSection.selectedFolderId()
        if selected_folder_id is None:
            self._view.page.heroSection.showStatusMessage(
                "Selecciona una biblioteca guardada para activarla."
            )
            return

        try:
            local_folder = self._local_folder_view_model.activate_folder(selected_folder_id)
        except (TypeError, ValueError) as exc:
            self._view.page.heroSection.showStatusMessage(str(exc))
            return

        self._load_folders()
        self._view.page.heroSection.showStatusMessage(
            f'Ahora estas trabajando con la biblioteca "{local_folder.display_name}".'
        )

    def _handle_save_playlist(self) -> None:
        try:
            youtube_playlist = self._youtube_playlist_view_model.define_main_playlist(
                self._view.page.youtubePlaylistsSection.playlistUrl()
            )
        except ValueError as exc:
            self._view.page.heroSection.showStatusMessage(str(exc))
            return

        self._load_playlists()
        self._view.page.heroSection.showStatusMessage(
            f'Playlist principal "{youtube_playlist.title}" guardada y activada correctamente.'
        )

    def _handle_activate_playlist(self) -> None:
        selected_playlist_id = self._view.page.youtubePlaylistsSection.selectedPlaylistId()
        if selected_playlist_id is None:
            self._view.page.heroSection.showStatusMessage(
                "Selecciona una playlist guardada para activarla."
            )
            return

        try:
            youtube_playlist = self._youtube_playlist_view_model.activate_playlist(
                selected_playlist_id
            )
        except (TypeError, ValueError) as exc:
            self._view.page.heroSection.showStatusMessage(str(exc))
            return

        self._load_playlists()
        self._view.page.heroSection.showStatusMessage(
            f'Ahora estas comparando contra la playlist "{youtube_playlist.title}".'
        )

    def _handle_create_term(self) -> None:
        try:
            created_term = self._ignored_terms_view_model.create_term(
                self._view.page.ignoredTermsSection.termText(),
                self._view.page.ignoredTermsSection.termScope(),
                self._view.page.ignoredTermsSection.termLanguage(),
            )
        except ValueError as exc:
            self._view.page.heroSection.showStatusMessage(str(exc))
            return

        self._view.page.ignoredTermsSection.clearTermInput()
        self._load_terms()
        self._view.page.heroSection.showStatusMessage(
            f'Termino "{created_term.term}" guardado para el scope "{created_term.scope}".'
        )
