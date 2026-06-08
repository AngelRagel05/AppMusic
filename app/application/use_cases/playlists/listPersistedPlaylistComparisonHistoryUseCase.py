from __future__ import annotations

from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.playlists.repositories.playlistComparisonRepository import (
    PlaylistComparisonRepository,
)
from app.domain.playlists.repositories.playlistComparisonResultRepository import (
    PlaylistComparisonResultRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.shared.constants.comparison import ComparisonStatus


class ListPersistedPlaylistComparisonHistoryUseCase:
    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        local_folder_repository: LocalFolderRepository,
        playlist_comparison_repository: PlaylistComparisonRepository,
        playlist_comparison_result_repository: PlaylistComparisonResultRepository,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._local_folder_repository = local_folder_repository
        self._playlist_comparison_repository = playlist_comparison_repository
        self._playlist_comparison_result_repository = playlist_comparison_result_repository

    def execute(self, limit: int = 5) -> list[PlaylistComparisonHistoryEntryDto]:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        active_local_folder = self._local_folder_repository.get_active()
        if (
            active_youtube_playlist is None
            or active_youtube_playlist.id is None
            or active_local_folder is None
            or active_local_folder.id is None
        ):
            return []

        comparisons = self._playlist_comparison_repository.list_for_scope(
            active_youtube_playlist.id,
            active_local_folder.id,
            limit=limit,
        )
        history_entries: list[PlaylistComparisonHistoryEntryDto] = []
        for comparison in comparisons:
            if comparison.id is None or comparison.compared_at is None:
                continue
            comparison_rows = self._playlist_comparison_result_repository.list_by_comparison(
                comparison.id
            )
            history_entries.append(
                PlaylistComparisonHistoryEntryDto(
                    comparison_id=comparison.id,
                    compared_at=comparison.compared_at,
                    found_count=sum(
                        1
                        for row in comparison_rows
                        if row.match_status == ComparisonStatus.FOUND.value
                    ),
                    missing_count=sum(
                        1
                        for row in comparison_rows
                        if row.match_status == ComparisonStatus.MISSING.value
                    ),
                    possible_match_count=sum(
                        1
                        for row in comparison_rows
                        if row.match_status == ComparisonStatus.POSSIBLE_MATCH.value
                    ),
                    total_compared=len(comparison_rows),
                )
            )
        return history_entries
