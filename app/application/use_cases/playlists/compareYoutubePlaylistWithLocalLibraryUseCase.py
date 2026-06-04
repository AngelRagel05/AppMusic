from __future__ import annotations

from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)


class CompareYoutubePlaylistWithLocalLibraryUseCase:
    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        youtube_playlist_item_repository: YoutubePlaylistItemRepository,
        local_song_repository: LocalSongRepository,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._youtube_playlist_item_repository = youtube_playlist_item_repository
        self._local_song_repository = local_song_repository

    def execute(self) -> None:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        if active_youtube_playlist is None or active_youtube_playlist.id is None:
            raise ValueError("No hay una playlist principal activa para comparar.")

        self._youtube_playlist_item_repository.list_by_playlist(active_youtube_playlist.id)
        raise NotImplementedError(
            "Pendiente de implementar el matching entre la playlist de YouTube y la biblioteca local."
        )
