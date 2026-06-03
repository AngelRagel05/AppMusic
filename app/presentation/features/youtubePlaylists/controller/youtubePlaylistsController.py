from __future__ import annotations

from collections.abc import Callable

from app.presentation.features.youtubePlaylists.ui.youtubePlaylistsPage.youtubePlaylistsPage import (
    YoutubePlaylistsPage,
)
from app.presentation.features.youtubePlaylists.viewmodel.youtubePlaylistViewModel import (
    YoutubePlaylistViewModel,
)


class YoutubePlaylistsController:
    def __init__(
        self,
        page: YoutubePlaylistsPage,
        view_model: YoutubePlaylistViewModel,
        show_page: Callable[[str, bool], None],
        on_state_changed: Callable[[], None],
        on_action_recorded: Callable[[str], None],
        on_active_playlist_changed: Callable[[str], None],
    ) -> None:
        self._page = page
        self._view_model = view_model
        self._show_page = show_page
        self._on_state_changed = on_state_changed
        self._on_action_recorded = on_action_recorded
        self._on_active_playlist_changed = on_active_playlist_changed
        self._editing_playlist_id: int | None = None

    def bindEvents(self) -> None:
        self._page.onSavePlaylistRequested(self._handleSavePlaylist)
        self._page.onActivatePlaylistRequested(self._handleActivatePlaylistById)
        self._page.onEditPlaylistRequested(self._handleEditPlaylistById)
        self._page.onDeletePlaylistRequested(self._handleDeletePlaylistById)

    def load(self) -> None:
        youtube_playlists, active_playlist = self._view_model.refreshState()
        self._page.showPlaylists(youtube_playlists)
        self._page.showActivePlaylist(active_playlist)
        active_playlist_title = (
            active_playlist.title if active_playlist is not None else "Sin playlist"
        )
        self._on_active_playlist_changed(active_playlist_title)
        self._on_state_changed()

    def activePlaylist(self):
        return self._view_model.load_active_playlist()

    def _handleSavePlaylist(self) -> None:
        try:
            if self._editing_playlist_id is None:
                youtube_playlist = self._view_model.define_main_playlist(
                    self._page.playlistUrl(),
                    self._page.playlistTitle(),
                )
                message = (
                    f'Playlist principal "{youtube_playlist.title}" guardada y activada correctamente.'
                )
            else:
                youtube_playlist = self._view_model.update_playlist(
                    self._editing_playlist_id,
                    self._page.playlistUrl(),
                    self._page.playlistTitle(),
                )
                message = f'Playlist "{youtube_playlist.title}" actualizada correctamente.'
        except ValueError as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        self._editing_playlist_id = None
        self._page.clearForm()
        self._renderState()
        self._page.showStatusMessage(message, tone="success")
        self._on_action_recorded(message)

    def _handleActivatePlaylistById(self, selected_playlist_id: int) -> None:
        try:
            youtube_playlist = self._view_model.activate_playlist(selected_playlist_id)
        except (TypeError, ValueError) as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        self._renderState()
        self._page.showStatusMessage(
            f'Ahora estas comparando contra la playlist "{youtube_playlist.title}".',
            tone="success",
        )
        self._on_action_recorded(
            f'Playlist activa cambiada a "{youtube_playlist.title}".'
        )

    def _handleEditPlaylistById(self, youtube_playlist_id: int) -> None:
        selected_playlist = self._view_model.find_playlist_by_id(youtube_playlist_id)
        if selected_playlist is None:
            self._page.showStatusMessage(
                "La playlist seleccionada no existe.",
                tone="error",
            )
            return

        self._editing_playlist_id = selected_playlist.id
        self._page.setPlaylistTitle(selected_playlist.title)
        self._page.setPlaylistUrl(selected_playlist.playlist_url)
        self._page.setSaveMode(True)
        self._show_page("youtubePlaylists", True)
        self._page.showStatusMessage(
            f'Editando la playlist "{selected_playlist.title}".',
            tone="info",
        )

    def _handleDeletePlaylistById(self, youtube_playlist_id: int) -> None:
        selected_playlist = self._view_model.find_playlist_by_id(youtube_playlist_id)
        if selected_playlist is None:
            self._page.showStatusMessage(
                "La playlist seleccionada no existe.",
                tone="error",
            )
            return

        try:
            self._view_model.delete_playlist(selected_playlist.id)
        except ValueError as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_playlist_id == selected_playlist.id:
            self._editing_playlist_id = None
            self._page.clearForm()
        self._renderState()
        self._page.showStatusMessage(
            f'Playlist "{selected_playlist.title}" eliminada correctamente.',
            tone="success",
        )
        self._on_action_recorded(
            f'Playlist "{selected_playlist.title}" eliminada.'
        )

    def _renderState(self) -> None:
        youtubePlaylists = self._view_model.load_playlists()
        activePlaylist = self._view_model.load_active_playlist()
        self._page.showPlaylists(youtubePlaylists)
        self._page.showActivePlaylist(activePlaylist)
        activePlaylistTitle = (
            activePlaylist.title if activePlaylist is not None else "Sin playlist"
        )
        self._on_active_playlist_changed(activePlaylistTitle)
        self._on_state_changed()
