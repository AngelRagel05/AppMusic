from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.playlists.entities.youtubePlaylist import YoutubePlaylist


class YoutubePlaylistRepository(ABC):
    @abstractmethod
    def get_active(self) -> YoutubePlaylist | None:
        raise NotImplementedError

    @abstractmethod
    def save_as_active(
        self,
        playlist_url: str,
        external_playlist_id: str,
        title: str,
    ) -> YoutubePlaylist:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[YoutubePlaylist]:
        raise NotImplementedError

    @abstractmethod
    def activate(self, youtube_playlist_id: int) -> YoutubePlaylist:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        youtube_playlist_id: int,
        playlist_url: str,
        external_playlist_id: str,
        title: str,
    ) -> YoutubePlaylist:
        raise NotImplementedError

    @abstractmethod
    def delete(self, youtube_playlist_id: int) -> None:
        raise NotImplementedError
