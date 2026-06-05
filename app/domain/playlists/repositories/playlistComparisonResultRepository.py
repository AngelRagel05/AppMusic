from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.playlists.entities.playlistComparisonResult import (
    PlaylistComparisonResult,
)


class PlaylistComparisonResultRepository(ABC):
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
