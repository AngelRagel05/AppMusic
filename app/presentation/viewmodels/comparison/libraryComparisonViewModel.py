from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.youtubePlaylistItemDto import YoutubePlaylistItemDto
from app.application.use_cases import (
    ListActiveLocalSongsUseCase,
    ListActiveYoutubePlaylistItemsUseCase,
)


class LibraryComparisonViewModel:
    def __init__(
        self,
        list_active_local_songs_use_case: ListActiveLocalSongsUseCase,
        list_active_youtube_playlist_items_use_case: ListActiveYoutubePlaylistItemsUseCase,
    ) -> None:
        self._list_active_local_songs_use_case = list_active_local_songs_use_case
        self._list_active_youtube_playlist_items_use_case = (
            list_active_youtube_playlist_items_use_case
        )
        self._local_songs_cache: list[LocalSongDto] = []
        self._youtube_playlist_items_cache: list[YoutubePlaylistItemDto] = []

    def refreshState(self) -> tuple[list[LocalSongDto], list[YoutubePlaylistItemDto]]:
        local_songs = self._list_active_local_songs_use_case.execute()
        youtube_playlist_items = (
            self._list_active_youtube_playlist_items_use_case.execute()
        )
        self._local_songs_cache = list(local_songs)
        self._youtube_playlist_items_cache = list(youtube_playlist_items)
        return local_songs, youtube_playlist_items

    def load_local_songs(self) -> list[LocalSongDto]:
        if not self._local_songs_cache and not self._youtube_playlist_items_cache:
            self.refreshState()
        return list(self._local_songs_cache)

    def load_youtube_playlist_items(self) -> list[YoutubePlaylistItemDto]:
        if not self._local_songs_cache and not self._youtube_playlist_items_cache:
            self.refreshState()
        return list(self._youtube_playlist_items_cache)
