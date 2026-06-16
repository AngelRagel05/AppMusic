from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.playlists.entities.playlistComparison import PlaylistComparison


class PlaylistComparisonRepository(ABC):
    @abstractmethod
    def find_by_id(
        self,
        playlist_comparison_id: int,
    ) -> PlaylistComparison | None:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        youtube_playlist_imported_at=None,
        local_library_scanned_at=None,
        youtube_playlist_state_fingerprint: str | None = None,
        local_library_state_fingerprint: str | None = None,
        ignored_terms_version: str | None = None,
        matching_rules_version: str | None = None,
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

    @abstractmethod
    def list_excess_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        keep_latest: int,
    ) -> list[PlaylistComparison]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_ids(
        self,
        playlist_comparison_ids: list[int],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError
