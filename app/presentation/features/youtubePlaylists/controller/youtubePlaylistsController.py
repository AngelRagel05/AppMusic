from __future__ import annotations

from collections.abc import Callable

from app.presentation.features.youtubePlaylists.viewmodel.youtubePlaylistViewModel import (
    YoutubePlaylistViewModel,
)
from app.presentation.shell.mainWindow.mainWindow import MainWindow


class YoutubePlaylistsController:
    def __init__(
        self,
        view: MainWindow,
        view_model: YoutubePlaylistViewModel,
        on_state_changed: Callable[[], None],
        on_action_recorded: Callable[[str], None],
    ) -> None:
        self._view = view
        self._view_model = view_model
        self._on_state_changed = on_state_changed
        self._on_action_recorded = on_action_recorded
        self._editing_playlist_id: int | None = None

    def bindEvents(self) -> None:
        section = self._view.page.youtubePlaylistsSection
        section.savePlaylistButton.clicked.connect(self._handleSavePlaylist)
        section.activateRequested.connect(self._handleActivatePlaylistById)
        section.editRequested.connect(self._handleEditPlaylistById)
        section.deleteRequested.connect(self._handleDeletePlaylistById)

    def load(self) -> None:
        youtube_playlists = self._view_model.load_playlists()
        active_playlist = self._view_model.load_active_playlist()
        self._view.page.youtubePlaylistsSection.showPlaylists(youtube_playlists)
        self._view.page.youtubePlaylistsSection.showActivePlaylist(active_playlist)
        active_playlist_title = (
            active_playlist.title if active_playlist is not None else "Sin playlist"
        )
        self._view.page.setActivePlaylistTitle(active_playlist_title)
        self._on_state_changed()

    def activePlaylist(self):
        return self._view_model.load_active_playlist()

    def _handleSavePlaylist(self) -> None:
        try:
            if self._editing_playlist_id is None:
                youtube_playlist = self._view_model.define_main_playlist(
                    self._view.page.youtubePlaylistsSection.playlistUrl(),
                    self._view.page.youtubePlaylistsSection.playlistTitle(),
                )
                message = (
                    f'Playlist principal "{youtube_playlist.title}" guardada y activada correctamente.'
                )
            else:
                youtube_playlist = self._view_model.update_playlist(
                    self._editing_playlist_id,
                    self._view.page.youtubePlaylistsSection.playlistUrl(),
                    self._view.page.youtubePlaylistsSection.playlistTitle(),
                )
                message = f'Playlist "{youtube_playlist.title}" actualizada correctamente.'
        except ValueError as exc:
            self._view.page.youtubePlaylistsSection.showStatusMessage(str(exc), tone="error")
            return

        self._editing_playlist_id = None
        self._view.page.youtubePlaylistsSection.clearForm()
        self.load()
        self._view.page.youtubePlaylistsSection.showStatusMessage(message, tone="success")
        self._on_action_recorded(message)

    def _handleActivatePlaylistById(self, selected_playlist_id: int) -> None:
        try:
            youtube_playlist = self._view_model.activate_playlist(selected_playlist_id)
        except (TypeError, ValueError) as exc:
            self._view.page.youtubePlaylistsSection.showStatusMessage(str(exc), tone="error")
            return

        self.load()
        self._view.page.youtubePlaylistsSection.showStatusMessage(
            f'Ahora estas comparando contra la playlist "{youtube_playlist.title}".',
            tone="success",
        )
        self._on_action_recorded(
            f'Playlist activa cambiada a "{youtube_playlist.title}".'
        )

    def _handleEditPlaylistById(self, youtube_playlist_id: int) -> None:
        selected_playlist = self._selectedPlaylistById(youtube_playlist_id)
        if selected_playlist is None:
            self._view.page.youtubePlaylistsSection.showStatusMessage(
                "La playlist seleccionada no existe.",
                tone="error",
            )
            return

        self._editing_playlist_id = selected_playlist.id
        self._view.page.youtubePlaylistsSection.setPlaylistTitle(selected_playlist.title)
        self._view.page.youtubePlaylistsSection.setPlaylistUrl(selected_playlist.playlist_url)
        self._view.page.youtubePlaylistsSection.setSaveMode(True)
        self._view.page.showPage("youtubePlaylists", focus_input=True)
        self._view.page.youtubePlaylistsSection.showStatusMessage(
            f'Editando la playlist "{selected_playlist.title}".',
            tone="info",
        )

    def _handleDeletePlaylistById(self, youtube_playlist_id: int) -> None:
        selected_playlist = self._selectedPlaylistById(youtube_playlist_id)
        if selected_playlist is None:
            self._view.page.youtubePlaylistsSection.showStatusMessage(
                "La playlist seleccionada no existe.",
                tone="error",
            )
            return

        try:
            self._view_model.delete_playlist(selected_playlist.id)
        except ValueError as exc:
            self._view.page.youtubePlaylistsSection.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_playlist_id == selected_playlist.id:
            self._editing_playlist_id = None
            self._view.page.youtubePlaylistsSection.clearForm()
        self.load()
        self._view.page.youtubePlaylistsSection.showStatusMessage(
            f'Playlist "{selected_playlist.title}" eliminada correctamente.',
            tone="success",
        )
        self._on_action_recorded(
            f'Playlist "{selected_playlist.title}" eliminada.'
        )

    def _selectedPlaylistById(self, youtube_playlist_id: int):
        return next(
            (
                youtube_playlist
                for youtube_playlist in self._view_model.load_playlists()
                if youtube_playlist.id == youtube_playlist_id
            ),
            None,
        )
