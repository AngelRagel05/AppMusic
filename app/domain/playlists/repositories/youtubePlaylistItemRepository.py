from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem


class YoutubePlaylistItemRepository(ABC):
    @abstractmethod
    def list_by_playlist(self, youtube_playlist_id: int) -> list[YoutubePlaylistItem]:
        raise NotImplementedError

    @abstractmethod
    def replace_for_playlist(
        self,
        youtube_playlist_id: int,
        items: list[YoutubePlaylistItem],
    ) -> list[YoutubePlaylistItem]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_playlist(self, youtube_playlist_id: int) -> None:
        raise NotImplementedError
