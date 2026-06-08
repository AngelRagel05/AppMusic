from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.playlists.entities.playlistComparison import PlaylistComparison


class PlaylistComparisonRepository(ABC):
    @abstractmethod
    def create(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> PlaylistComparison:
        raise NotImplementedError

    @abstractmethod
    def find_latest_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> PlaylistComparison | None:
        raise NotImplementedError

    @abstractmethod
    def list_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        limit: int,
    ) -> list[PlaylistComparison]:
        raise NotImplementedError
