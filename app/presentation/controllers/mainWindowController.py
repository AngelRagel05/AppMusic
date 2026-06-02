from __future__ import annotations

from tkinter import filedialog

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
        self._editing_local_folder_id: int | None = None
        self._editing_youtube_playlist_id: int | None = None
        self._last_action_message = "Todavia no hay acciones registradas"

    def initialize(self) -> None:
        page = self._view.page
        page.localLibrariesSection.browseFolderButton.clicked.connect(self._handle_browse_folder)
        page.localLibrariesSection.saveFolderButton.clicked.connect(self._handle_save_folder)
        page.localLibrariesSection.activateRequested.connect(self._handle_activate_folder_by_id)
        page.localLibrariesSection.editRequested.connect(self._handle_edit_folder_by_id)
        page.localLibrariesSection.deleteRequested.connect(self._handle_delete_folder_by_id)
        page.youtubePlaylistsSection.savePlaylistButton.clicked.connect(
            self._handle_save_playlist
        )
        page.youtubePlaylistsSection.activateRequested.connect(
            self._handle_activate_playlist_by_id
        )
        page.youtubePlaylistsSection.editRequested.connect(self._handle_edit_playlist_by_id)
        page.youtubePlaylistsSection.deleteRequested.connect(
            self._handle_delete_playlist_by_id
        )
        page.ignoredTermsSection.createButton.clicked.connect(self._handle_create_term)

        self._load_folders()
        self._load_playlists()
        self._load_terms()
        self._view.page.setLastAction(self._last_action_message)

    def _load_folders(self) -> None:
        local_folders = self._local_folder_view_model.load_folders()
        active_folder = self._local_folder_view_model.load_active_folder()
        self._view.page.localLibrariesSection.showFolders(local_folders)
        self._view.page.localLibrariesSection.showActiveFolder(active_folder)
        active_folder_name = (
            active_folder.display_name if active_folder is not None else "Sin biblioteca"
        )
        self._view.page.setActiveFolderName(active_folder_name)
        self._view.page.setSongCount("Sin escanear")
        self._update_sync_status()

    def _load_playlists(self) -> None:
        youtube_playlists = self._youtube_playlist_view_model.load_playlists()
        active_playlist = self._youtube_playlist_view_model.load_active_playlist()
        self._view.page.youtubePlaylistsSection.showPlaylists(youtube_playlists)
        self._view.page.youtubePlaylistsSection.showActivePlaylist(active_playlist)
        active_playlist_title = (
            active_playlist.title if active_playlist is not None else "Sin playlist"
        )
        self._view.page.setActivePlaylistTitle(active_playlist_title)
        self._update_sync_status()

    def _load_terms(self) -> None:
        ignored_terms = self._ignored_terms_view_model.load_terms()
        self._view.page.ignoredTermsSection.showTerms(ignored_terms)

    def _update_sync_status(self) -> None:
        active_folder = self._local_folder_view_model.load_active_folder()
        active_playlist = self._youtube_playlist_view_model.load_active_playlist()
        if active_folder is not None and active_playlist is not None:
            self._view.page.setSyncStatus("Listo", state="ready")
            return

        self._view.page.setSyncStatus("Pendiente", state="idle")

    def _handle_browse_folder(self) -> None:
        selected_folder = filedialog.askdirectory(
            parent=self._view.window,
            title="Seleccionar carpeta principal",
            initialdir=self._view.page.localLibrariesSection.folderPath() or None,
        )
        if selected_folder:
            self._view.page.localLibrariesSection.setFolderPath(selected_folder)

    def _handle_save_folder(self) -> None:
        try:
            if self._editing_local_folder_id is None:
                local_folder = self._local_folder_view_model.define_main_folder(
                    self._view.page.localLibrariesSection.folderPath()
                )
                message = (
                    f'Biblioteca "{local_folder.display_name}" guardada y activada correctamente.'
                )
            else:
                local_folder = self._local_folder_view_model.update_folder(
                    self._editing_local_folder_id,
                    self._view.page.localLibrariesSection.folderPath(),
                )
                message = f'Biblioteca "{local_folder.display_name}" actualizada correctamente.'
        except ValueError as exc:
            self._view.page.localLibrariesSection.showStatusMessage(str(exc), tone="error")
            return

        self._editing_local_folder_id = None
        self._view.page.localLibrariesSection.clearForm()
        self._load_folders()
        self._view.page.localLibrariesSection.showStatusMessage(message, tone="success")
        self._record_last_action(message)

    def _handle_activate_folder_by_id(self, selected_folder_id: int) -> None:
        try:
            local_folder = self._local_folder_view_model.activate_folder(selected_folder_id)
        except (TypeError, ValueError) as exc:
            self._view.page.localLibrariesSection.showStatusMessage(str(exc), tone="error")
            return

        self._load_folders()
        self._view.page.localLibrariesSection.showStatusMessage(
            f'Ahora estas trabajando con la biblioteca "{local_folder.display_name}".',
            tone="success",
        )
        self._record_last_action(
            f'Biblioteca activa cambiada a "{local_folder.display_name}".'
        )

    def _handle_save_playlist(self) -> None:
        try:
            if self._editing_youtube_playlist_id is None:
                youtube_playlist = self._youtube_playlist_view_model.define_main_playlist(
                    self._view.page.youtubePlaylistsSection.playlistUrl(),
                    self._view.page.youtubePlaylistsSection.playlistTitle(),
                )
                message = (
                    f'Playlist principal "{youtube_playlist.title}" guardada y activada correctamente.'
                )
            else:
                youtube_playlist = self._youtube_playlist_view_model.update_playlist(
                    self._editing_youtube_playlist_id,
                    self._view.page.youtubePlaylistsSection.playlistUrl(),
                    self._view.page.youtubePlaylistsSection.playlistTitle(),
                )
                message = f'Playlist "{youtube_playlist.title}" actualizada correctamente.'
        except ValueError as exc:
            self._view.page.youtubePlaylistsSection.showStatusMessage(str(exc), tone="error")
            return

        self._editing_youtube_playlist_id = None
        self._view.page.youtubePlaylistsSection.clearForm()
        self._load_playlists()
        self._view.page.youtubePlaylistsSection.showStatusMessage(message, tone="success")
        self._record_last_action(message)

    def _handle_activate_playlist_by_id(self, selected_playlist_id: int) -> None:
        try:
            youtube_playlist = self._youtube_playlist_view_model.activate_playlist(
                selected_playlist_id
            )
        except (TypeError, ValueError) as exc:
            self._view.page.youtubePlaylistsSection.showStatusMessage(str(exc), tone="error")
            return

        self._load_playlists()
        self._view.page.youtubePlaylistsSection.showStatusMessage(
            f'Ahora estas comparando contra la playlist "{youtube_playlist.title}".',
            tone="success",
        )
        self._record_last_action(
            f'Playlist activa cambiada a "{youtube_playlist.title}".'
        )

    def _handle_edit_folder_by_id(self, local_folder_id: int) -> None:
        selected_folder = self._selected_local_folder_by_id(local_folder_id)
        if selected_folder is None:
            self._view.page.localLibrariesSection.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        self._editing_local_folder_id = selected_folder.id
        self._view.page.localLibrariesSection.setFolderPath(selected_folder.path)
        self._view.page.localLibrariesSection.setSaveMode(True)
        self._view.page.showPage("libraries", focus_input=True)
        self._view.page.localLibrariesSection.showStatusMessage(
            f'Editando la biblioteca "{selected_folder.display_name}".',
            tone="info",
        )

    def _handle_delete_folder_by_id(self, local_folder_id: int) -> None:
        selected_folder = self._selected_local_folder_by_id(local_folder_id)
        if selected_folder is None:
            self._view.page.localLibrariesSection.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        try:
            self._local_folder_view_model.delete_folder(selected_folder.id)
        except ValueError as exc:
            self._view.page.localLibrariesSection.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_local_folder_id == selected_folder.id:
            self._editing_local_folder_id = None
            self._view.page.localLibrariesSection.clearForm()
        self._load_folders()
        self._view.page.localLibrariesSection.showStatusMessage(
            f'Biblioteca "{selected_folder.display_name}" eliminada correctamente.',
            tone="success",
        )
        self._record_last_action(
            f'Biblioteca "{selected_folder.display_name}" eliminada.'
        )

    def _handle_edit_playlist_by_id(self, youtube_playlist_id: int) -> None:
        selected_playlist = self._selected_youtube_playlist_by_id(youtube_playlist_id)
        if selected_playlist is None:
            self._view.page.youtubePlaylistsSection.showStatusMessage(
                "La playlist seleccionada no existe.",
                tone="error",
            )
            return

        self._editing_youtube_playlist_id = selected_playlist.id
        self._view.page.youtubePlaylistsSection.setPlaylistTitle(selected_playlist.title)
        self._view.page.youtubePlaylistsSection.setPlaylistUrl(selected_playlist.playlist_url)
        self._view.page.youtubePlaylistsSection.setSaveMode(True)
        self._view.page.showPage("playlists", focus_input=True)
        self._view.page.youtubePlaylistsSection.showStatusMessage(
            f'Editando la playlist "{selected_playlist.title}".',
            tone="info",
        )

    def _handle_delete_playlist_by_id(self, youtube_playlist_id: int) -> None:
        selected_playlist = self._selected_youtube_playlist_by_id(youtube_playlist_id)
        if selected_playlist is None:
            self._view.page.youtubePlaylistsSection.showStatusMessage(
                "La playlist seleccionada no existe.",
                tone="error",
            )
            return

        try:
            self._youtube_playlist_view_model.delete_playlist(selected_playlist.id)
        except ValueError as exc:
            self._view.page.youtubePlaylistsSection.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_youtube_playlist_id == selected_playlist.id:
            self._editing_youtube_playlist_id = None
            self._view.page.youtubePlaylistsSection.clearForm()
        self._load_playlists()
        self._view.page.youtubePlaylistsSection.showStatusMessage(
            f'Playlist "{selected_playlist.title}" eliminada correctamente.',
            tone="success",
        )
        self._record_last_action(
            f'Playlist "{selected_playlist.title}" eliminada.'
        )

    def _selected_local_folder_by_id(self, local_folder_id: int):
        return next(
            (
                local_folder
                for local_folder in self._local_folder_view_model.load_folders()
                if local_folder.id == local_folder_id
            ),
            None,
        )

    def _selected_youtube_playlist_by_id(self, youtube_playlist_id: int):
        return next(
            (
                youtube_playlist
                for youtube_playlist in self._youtube_playlist_view_model.load_playlists()
                if youtube_playlist.id == youtube_playlist_id
            ),
            None,
        )

    def _handle_create_term(self) -> None:
        try:
            created_term = self._ignored_terms_view_model.create_term(
                self._view.page.ignoredTermsSection.termText(),
                self._view.page.ignoredTermsSection.termScope(),
                self._view.page.ignoredTermsSection.termLanguage(),
            )
        except ValueError as exc:
            self._view.page.ignoredTermsSection.showStatusMessage(str(exc), tone="error")
            return

        self._view.page.ignoredTermsSection.clearTermInput()
        self._load_terms()
        message = f'Termino "{created_term.term}" guardado para el scope "{created_term.scope}".'
        self._view.page.ignoredTermsSection.showStatusMessage(message, tone="success")
        self._record_last_action(message)

    def _record_last_action(self, message: str) -> None:
        self._last_action_message = message
        self._view.page.setLastAction(message)
