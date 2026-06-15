from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.playlists.entities.playlistComparisonResult import (
    PlaylistComparisonResult,
)


class PlaylistComparisonResultRepository(ABC):
    @abstractmethod
    def find_by_comparison_item(
        self,
        playlist_comparison_id: int,
        youtube_playlist_item_id: int,
    ) -> PlaylistComparisonResult | None:
        raise NotImplementedError

    @abstractmethod
    def save_for_comparison(
        self,
        playlist_comparison_id: int,
        results: list[PlaylistComparisonResult],
    ) -> list[PlaylistComparisonResult]:
        raise NotImplementedError

    @abstractmethod
    def list_by_comparison(
        self,
        playlist_comparison_id: int,
    ) -> list[PlaylistComparisonResult]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_comparison_id(
        self,
        playlist_comparison_id: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_match_decision(
        self,
        *,
        playlist_comparison_id: int,
        youtube_playlist_item_id: int,
        match_status: str,
        local_song_id: int | None,
        matched_by: str,
    ) -> PlaylistComparisonResult:
        raise NotImplementedError
