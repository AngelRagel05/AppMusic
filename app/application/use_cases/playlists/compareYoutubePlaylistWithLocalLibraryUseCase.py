from __future__ import annotations

from datetime import UTC, datetime

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.playlists.entities.playlistComparisonResult import (
    PlaylistComparisonResult,
)
from app.domain.playlists.services import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
    matchPersistedPlaylistItemToLocalSongs,
)
from app.domain.playlists.repositories.playlistComparisonRepository import (
    PlaylistComparisonRepository,
)
from app.domain.playlists.repositories.playlistComparisonResultRepository import (
    PlaylistComparisonResultRepository,
)
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.shared.constants.comparison import ComparisonStatus


class CompareYoutubePlaylistWithLocalLibraryUseCase:
    SNAPSHOT_RETENTION_LIMIT = 3

    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        youtube_playlist_item_repository: YoutubePlaylistItemRepository,
        local_folder_repository: LocalFolderRepository,
        local_song_repository: LocalSongRepository,
        playlist_comparison_repository: PlaylistComparisonRepository,
        playlist_comparison_result_repository: PlaylistComparisonResultRepository,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._youtube_playlist_item_repository = youtube_playlist_item_repository
        self._local_folder_repository = local_folder_repository
        self._local_song_repository = local_song_repository
        self._playlist_comparison_repository = playlist_comparison_repository
        self._playlist_comparison_result_repository = playlist_comparison_result_repository

    def execute(self) -> PlaylistComparisonResultDto:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        if active_youtube_playlist is None or active_youtube_playlist.id is None:
            raise ValueError("No hay una playlist principal activa para comparar.")

        active_local_folder = self._local_folder_repository.get_active()
        if active_local_folder is None or active_local_folder.id is None:
            raise ValueError("No hay una biblioteca local activa para comparar.")

        youtube_playlist_items = self._youtube_playlist_item_repository.list_by_playlist(
            active_youtube_playlist.id
        )
        available_local_songs = [
            local_song
            for local_song in self._local_song_repository.list_by_folder(active_local_folder.id)
            if local_song.is_available
        ]
        comparable_local_songs = [
            self._buildComparableLocalSong(local_song)
            for local_song in available_local_songs
            if local_song.id is not None
        ]
        local_song_by_id = {
            local_song.id: local_song for local_song in available_local_songs if local_song.id is not None
        }

        comparison_items: list[PlaylistComparisonItemResultDto] = []
        match_result_by_item: dict[int, str | None] = {}
        for youtube_playlist_item in youtube_playlist_items:
            comparable_youtube_playlist_item = self._buildComparableYoutubePlaylistItem(
                youtube_playlist_item
            )
            match_result = matchPersistedPlaylistItemToLocalSongs(
                comparable_youtube_playlist_item,
                comparable_local_songs,
            )
            match_result_by_item[youtube_playlist_item.id or 0] = match_result.matched_by
            matched_local_song = (
                local_song_by_id.get(match_result.local_song.id)
                if match_result.local_song is not None
                else None
            )
            comparison_items.append(
                PlaylistComparisonItemResultDto(
                    youtube_playlist_item_id=youtube_playlist_item.id or 0,
                    local_song_id=matched_local_song.id if matched_local_song is not None else None,
                    comparison_status=match_result.comparison_status,
                    youtube_title=(
                        youtube_playlist_item.raw_title or youtube_playlist_item.normalized_title
                    ),
                    youtube_artist=(
                        youtube_playlist_item.raw_channel_name
                        or youtube_playlist_item.normalized_artist
                    ),
                    local_title=matched_local_song.title if matched_local_song is not None else None,
                    local_artist=matched_local_song.artist if matched_local_song is not None else None,
                    score=match_result.score,
                    reason=match_result.reason,
                    matched_by=match_result.matched_by,
                )
            )

        persisted_comparison = self._playlist_comparison_repository.create(
            active_youtube_playlist.id,
            active_local_folder.id,
        )
        self._playlist_comparison_result_repository.save_for_comparison(
            persisted_comparison.id or 0,
            [
                PlaylistComparisonResult(
                    playlist_comparison_id=persisted_comparison.id or 0,
                    youtube_playlist_item_id=item.youtube_playlist_item_id,
                    local_song_id=item.local_song_id,
                    match_status=item.comparison_status.value,
                    score=item.score,
                    matched_by=match_result_by_item[item.youtube_playlist_item_id],
                )
                for item in comparison_items
            ],
        )
        excess_comparisons = self._playlist_comparison_repository.list_excess_for_scope(
            active_youtube_playlist.id,
            active_local_folder.id,
            keep_latest=self.SNAPSHOT_RETENTION_LIMIT,
        )
        excess_comparison_ids = [
            comparison.id
            for comparison in excess_comparisons
            if comparison.id is not None
        ]
        for comparison_id in excess_comparison_ids:
            self._playlist_comparison_result_repository.delete_by_comparison_id(comparison_id)
        self._playlist_comparison_repository.delete_by_ids(excess_comparison_ids)
        self._playlist_comparison_repository.commit()

        summary = PlaylistComparisonSummaryDto(
            found_count=sum(
                1
                for item in comparison_items
                if item.comparison_status is ComparisonStatus.FOUND
            ),
            missing_count=sum(
                1
                for item in comparison_items
                if item.comparison_status is ComparisonStatus.MISSING
            ),
            possible_match_count=sum(
                1
                for item in comparison_items
                if item.comparison_status is ComparisonStatus.POSSIBLE_MATCH
            ),
            total_compared=len(comparison_items),
        )
        return PlaylistComparisonResultDto(
            summary=summary,
            items=comparison_items,
            playlist_comparison_id=persisted_comparison.id,
            last_compared_at=(
                persisted_comparison.compared_at or datetime.now(UTC)
            ),
        )

    def _buildComparableLocalSong(self, local_song) -> ComparableLocalSong:
        if local_song.id is None:
            raise ValueError("La cancion local comparable requiere un id persistido.")
        return ComparableLocalSong(
            id=local_song.id,
            title=local_song.title,
            artist=local_song.artist,
            duration_seconds=local_song.duration_seconds,
            is_available=local_song.is_available,
        )

    def _buildComparableYoutubePlaylistItem(self, youtube_playlist_item) -> ComparableYoutubePlaylistItem:
        if youtube_playlist_item.id is None:
            raise ValueError("El item de YouTube comparable requiere un id persistido.")
        return ComparableYoutubePlaylistItem(
            id=youtube_playlist_item.id,
            normalized_title=youtube_playlist_item.normalized_title,
            normalized_artist=youtube_playlist_item.normalized_artist,
            duration_seconds=youtube_playlist_item.duration_seconds,
        )
