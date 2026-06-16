from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.filters.repositories.ignoredTermRepository import IgnoredTermRepository
from app.domain.playlists.entities.playlistComparisonResult import (
    PlaylistComparisonResult,
)
from app.domain.playlists.services import (
    CandidateSelectionStage,
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
    MANUAL_USER_LINKED_LOCAL_SONG,
    MANUAL_USER_MARKED_FOUND,
    buildCandidateSelectionBatches,
    buildComparableLocalSongCandidateIndex,
    matchPersistedPlaylistItemToLocalSongs,
    shouldInvalidatePersistedFoundMatch,
)
from app.domain.playlists.repositories.playlistComparisonRepository import PlaylistComparisonRepository
from app.domain.playlists.repositories.playlistComparisonResultRepository import PlaylistComparisonResultRepository
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class IncrementalComparisonPlan:
    frozen_rows_by_item_id: dict[int, PlaylistComparisonResult]
    youtube_items_to_recompare: list[object]
    reserved_local_song_ids: set[int]


class CompareYoutubePlaylistWithLocalLibraryUseCase:
    SNAPSHOT_RETENTION_LIMIT = 3
    MATCHING_RULES_VERSION = "persisted_match_v5_real_incremental_snapshot"

    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        youtube_playlist_item_repository: YoutubePlaylistItemRepository,
        local_folder_repository: LocalFolderRepository,
        local_song_repository: LocalSongRepository,
        playlist_comparison_repository: PlaylistComparisonRepository,
        playlist_comparison_result_repository: PlaylistComparisonResultRepository,
        ignored_term_repository: IgnoredTermRepository | None = None,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._youtube_playlist_item_repository = youtube_playlist_item_repository
        self._local_folder_repository = local_folder_repository
        self._local_song_repository = local_song_repository
        self._playlist_comparison_repository = playlist_comparison_repository
        self._playlist_comparison_result_repository = playlist_comparison_result_repository
        self._ignored_term_repository = ignored_term_repository

    def execute(
        self,
        *,
        force_full_recompute: bool = False,
    ) -> PlaylistComparisonResultDto:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        if active_youtube_playlist is None or active_youtube_playlist.id is None:
            raise ValueError("No hay una playlist principal activa para comparar.")

        active_local_folder = self._local_folder_repository.get_active()
        if active_local_folder is None or active_local_folder.id is None:
            raise ValueError("No hay una biblioteca local activa para comparar.")

        youtube_playlist_items = self._youtube_playlist_item_repository.list_by_playlist(
            active_youtube_playlist.id
        )
        persisted_local_songs = self._local_song_repository.list_by_folder(active_local_folder.id)
        available_local_songs = [local_song for local_song in persisted_local_songs if local_song.is_available]
        comparable_local_songs = [
            self._buildComparableLocalSong(local_song)
            for local_song in available_local_songs
            if local_song.id is not None
        ]
        candidate_index = buildComparableLocalSongCandidateIndex(comparable_local_songs)
        local_song_by_id = {
            local_song.id: local_song for local_song in persisted_local_songs if local_song.id is not None
        }
        youtube_playlist_item_by_id = {
            youtube_playlist_item.id: youtube_playlist_item
            for youtube_playlist_item in youtube_playlist_items
            if youtube_playlist_item.id is not None
        }
        latest_persisted_comparison = self._playlist_comparison_repository.find_latest_for_scope(
            active_youtube_playlist.id,
            active_local_folder.id,
        )
        latest_results = (
            self._playlist_comparison_result_repository.list_by_comparison(
                latest_persisted_comparison.id
            )
            if latest_persisted_comparison is not None and latest_persisted_comparison.id is not None
            else []
        )
        current_ignored_terms_version = self._buildIgnoredTermsVersion()
        current_youtube_playlist_imported_at = self._buildSnapshotTimestamp(youtube_playlist_items)
        current_local_library_scanned_at = self._buildSnapshotTimestamp(persisted_local_songs)
        current_youtube_playlist_state_fingerprint = self._buildYoutubePlaylistStateFingerprint(
            youtube_playlist_items
        )
        current_local_library_state_fingerprint = self._buildLocalLibraryStateFingerprint(
            persisted_local_songs
        )

        comparison_items: list[PlaylistComparisonItemResultDto] = []
        match_result_by_item: dict[int, str | None] = {}
        incremental_plan = self._buildIncrementalComparisonPlan(
            latest_results=latest_results,
            latest_persisted_comparison=latest_persisted_comparison,
            youtube_playlist_items=youtube_playlist_items,
            youtube_playlist_item_by_id=youtube_playlist_item_by_id,
            local_song_by_id=local_song_by_id,
            current_ignored_terms_version=current_ignored_terms_version,
            force_full_recompute=force_full_recompute,
        )

        for youtube_playlist_item in youtube_playlist_items:
            frozen_row = incremental_plan.frozen_rows_by_item_id.get(youtube_playlist_item.id or 0)
            if frozen_row is not None:
                linked_local_song = (
                    local_song_by_id.get(frozen_row.local_song_id)
                    if frozen_row.local_song_id is not None
                    else None
                )
                comparison_items.append(
                    PlaylistComparisonItemResultDto(
                        youtube_playlist_item_id=frozen_row.youtube_playlist_item_id,
                        local_song_id=frozen_row.local_song_id,
                        comparison_status=ComparisonStatus(frozen_row.match_status),
                        youtube_title=(
                            youtube_playlist_item.raw_title or youtube_playlist_item.normalized_title
                        ),
                        youtube_artist=(
                            youtube_playlist_item.raw_channel_name
                            or youtube_playlist_item.normalized_artist
                        ),
                        local_title=linked_local_song.title if linked_local_song is not None else None,
                        local_artist=linked_local_song.artist if linked_local_song is not None else None,
                        score=float(frozen_row.score or 0.0),
                        reason=self._buildFrozenFoundReason(frozen_row.matched_by),
                        matched_by=frozen_row.matched_by,
                    )
                )
                match_result_by_item[frozen_row.youtube_playlist_item_id] = frozen_row.matched_by
                continue

        for youtube_playlist_item in incremental_plan.youtube_items_to_recompare:
            comparable_youtube_playlist_item = self._buildComparableYoutubePlaylistItem(
                youtube_playlist_item
            )
            match_result = self._matchWithCandidateStages(
                comparable_youtube_playlist_item,
                candidate_index,
                reserved_local_song_ids=incremental_plan.reserved_local_song_ids,
            )
            match_result_by_item[youtube_playlist_item.id or 0] = match_result.matched_by
            matched_local_song = (
                local_song_by_id.get(match_result.local_song.id)
                if match_result.local_song is not None
                else None
            )
            if (
                match_result.comparison_status is ComparisonStatus.FOUND
                and matched_local_song is not None
                and matched_local_song.id is not None
            ):
                incremental_plan.reserved_local_song_ids.add(matched_local_song.id)
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

        comparison_items_by_item_id = {
            item.youtube_playlist_item_id: item for item in comparison_items
        }
        comparison_items = [
            comparison_items_by_item_id[youtube_playlist_item.id or 0]
            for youtube_playlist_item in youtube_playlist_items
            if (youtube_playlist_item.id or 0) in comparison_items_by_item_id
        ]

        persisted_comparison = self._playlist_comparison_repository.create(
            active_youtube_playlist.id,
            active_local_folder.id,
            youtube_playlist_imported_at=current_youtube_playlist_imported_at,
            local_library_scanned_at=current_local_library_scanned_at,
            youtube_playlist_state_fingerprint=current_youtube_playlist_state_fingerprint,
            local_library_state_fingerprint=current_local_library_state_fingerprint,
            ignored_terms_version=current_ignored_terms_version,
            matching_rules_version=self.MATCHING_RULES_VERSION,
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

    def _buildIncrementalComparisonPlan(
        self,
        *,
        latest_results: list[PlaylistComparisonResult],
        latest_persisted_comparison,
        youtube_playlist_items: list[object],
        youtube_playlist_item_by_id: dict[int, object],
        local_song_by_id: dict[int, object],
        current_ignored_terms_version: str,
        force_full_recompute: bool,
    ) -> IncrementalComparisonPlan:
        if force_full_recompute:
            return IncrementalComparisonPlan(
                frozen_rows_by_item_id={},
                youtube_items_to_recompare=list(youtube_playlist_items),
                reserved_local_song_ids=set(),
            )

        frozen_rows_by_item_id = self._buildFrozenFoundRowsByItemId(
            latest_results=latest_results,
            latest_persisted_comparison=latest_persisted_comparison,
            youtube_playlist_item_by_id=youtube_playlist_item_by_id,
            local_song_by_id=local_song_by_id,
            current_ignored_terms_version=current_ignored_terms_version,
        )
        reserved_local_song_ids = {
            row.local_song_id
            for row in frozen_rows_by_item_id.values()
            if row.local_song_id is not None
        }
        youtube_items_to_recompare = [
            youtube_playlist_item
            for youtube_playlist_item in youtube_playlist_items
            if (youtube_playlist_item.id or 0) not in frozen_rows_by_item_id
        ]
        return IncrementalComparisonPlan(
            frozen_rows_by_item_id=frozen_rows_by_item_id,
            youtube_items_to_recompare=youtube_items_to_recompare,
            reserved_local_song_ids=reserved_local_song_ids,
        )

    def _matchWithCandidateStages(
        self,
        youtube_playlist_item: ComparableYoutubePlaylistItem,
        candidate_index,
        *,
        reserved_local_song_ids: set[int],
    ):
        candidate_batches = buildCandidateSelectionBatches(
            youtube_playlist_item,
            candidate_index,
            reserved_local_song_ids=reserved_local_song_ids,
        )
        last_match_result = None
        for candidate_batch in candidate_batches:
            last_match_result = matchPersistedPlaylistItemToLocalSongs(
                youtube_playlist_item,
                candidate_batch.local_songs,
            )
            if (
                candidate_batch.stage is CandidateSelectionStage.EXACT
                and last_match_result.comparison_status is ComparisonStatus.FOUND
            ):
                return last_match_result
            if (
                candidate_batch.stage is CandidateSelectionStage.VERY_SIMILAR
                and last_match_result.comparison_status is ComparisonStatus.FOUND
            ):
                return last_match_result
        if last_match_result is not None:
            return last_match_result
        return matchPersistedPlaylistItemToLocalSongs(youtube_playlist_item, ())

    def _buildFrozenFoundRowsByItemId(
        self,
        *,
        latest_results,
        latest_persisted_comparison,
        youtube_playlist_item_by_id: dict[int, object],
        local_song_by_id: dict[int, object],
        current_ignored_terms_version: str,
    ) -> dict[int, PlaylistComparisonResult]:
        if latest_persisted_comparison is None:
            return {}

        frozen_rows: dict[int, PlaylistComparisonResult] = {}
        for latest_result in latest_results:
            if latest_result.match_status != ComparisonStatus.FOUND.value:
                continue
            if latest_result.local_song_id is None:
                continue
            youtube_playlist_item = youtube_playlist_item_by_id.get(latest_result.youtube_playlist_item_id)
            local_song = local_song_by_id.get(latest_result.local_song_id)
            if youtube_playlist_item is None or local_song is None:
                continue
            if self._shouldInvalidateFrozenFoundRow(
                latest_result=latest_result,
                latest_persisted_comparison=latest_persisted_comparison,
                youtube_playlist_item=youtube_playlist_item,
                local_song=local_song,
                current_ignored_terms_version=current_ignored_terms_version,
            ):
                continue
            frozen_rows[latest_result.youtube_playlist_item_id] = latest_result
        return frozen_rows

    def _shouldInvalidateFrozenFoundRow(
        self,
        *,
        latest_result: PlaylistComparisonResult,
        latest_persisted_comparison,
        youtube_playlist_item,
        local_song,
        current_ignored_terms_version: str,
    ) -> bool:
        youtube_snapshot_timestamp = latest_persisted_comparison.youtube_playlist_imported_at
        local_snapshot_timestamp = latest_persisted_comparison.local_library_scanned_at
        persisted_ignored_terms_version = latest_persisted_comparison.ignored_terms_version
        persisted_matching_rules_version = latest_persisted_comparison.matching_rules_version
        if (
            youtube_snapshot_timestamp is None
            or local_snapshot_timestamp is None
            or not persisted_ignored_terms_version
            or not persisted_matching_rules_version
        ):
            return True
        if shouldInvalidatePersistedFoundMatch(
            persisted_dependencies=self._buildSnapshotDependenciesFingerprint(
                ignored_terms_version=persisted_ignored_terms_version,
                matching_rules_version=persisted_matching_rules_version,
            ),
            current_dependencies=self._buildSnapshotDependenciesFingerprint(
                ignored_terms_version=current_ignored_terms_version,
                matching_rules_version=self.MATCHING_RULES_VERSION,
            ),
            local_song_is_available=local_song.is_available,
        ):
            return True
        local_song_updated_at = self._normalizeTimestamp(
            local_song.updated_at or local_song.created_at
        )
        local_snapshot_timestamp = self._normalizeTimestamp(local_snapshot_timestamp)
        if local_song_updated_at is not None and local_song_updated_at > local_snapshot_timestamp:
            return True
        youtube_item_updated_at = self._normalizeTimestamp(
            youtube_playlist_item.updated_at or youtube_playlist_item.created_at
        )
        youtube_snapshot_timestamp = self._normalizeTimestamp(youtube_snapshot_timestamp)
        if youtube_item_updated_at is not None and youtube_item_updated_at > youtube_snapshot_timestamp:
            return True
        return False

    def _buildSnapshotDependenciesFingerprint(
        self,
        *,
        ignored_terms_version: str,
        matching_rules_version: str,
    ):
        from app.domain.playlists.services import ComparisonDependenciesFingerprint

        return ComparisonDependenciesFingerprint(
            youtube_playlist_version="snapshot_scoped",
            local_library_version="snapshot_scoped",
            ignored_terms_version=ignored_terms_version,
            matching_rules_version=matching_rules_version,
        )

    def _buildSnapshotTimestamp(self, items: list[object]) -> datetime:
        timestamps = [
            self._normalizeTimestamp(timestamp)
            for item in items
            for timestamp in [getattr(item, "updated_at", None) or getattr(item, "created_at", None)]
            if timestamp is not None
        ]
        if timestamps:
            return max(timestamps)
        return datetime.now(UTC)

    def _buildIgnoredTermsVersion(self) -> str:
        if self._ignored_term_repository is None:
            return "ignored_terms:untracked"
        serialized_terms = []
        for ignored_term in self._ignored_term_repository.list_all():
            serialized_terms.append(
                "|".join(
                    [
                        str(ignored_term.id or 0),
                        ignored_term.term,
                        ignored_term.scope,
                        ignored_term.language,
                        "1" if ignored_term.is_active else "0",
                        (
                            (ignored_term.updated_at or ignored_term.created_at).isoformat()
                            if (ignored_term.updated_at or ignored_term.created_at) is not None
                            else "na"
                        ),
                    ]
                )
            )
        digest = hashlib.sha1("\n".join(serialized_terms).encode("utf-8")).hexdigest()
        return f"ignored_terms:{digest}"

    def _buildYoutubePlaylistStateFingerprint(self, youtube_playlist_items: list[object]) -> str:
        serialized_items = []
        for youtube_playlist_item in sorted(
            youtube_playlist_items,
            key=lambda item: (
                getattr(item, "position", 0),
                getattr(item, "external_video_id", ""),
            ),
        ):
            serialized_items.append(
                "|".join(
                    [
                        str(getattr(youtube_playlist_item, "id", None) or 0),
                        getattr(youtube_playlist_item, "external_video_id", ""),
                        str(getattr(youtube_playlist_item, "position", 0)),
                        getattr(youtube_playlist_item, "normalized_title", ""),
                        getattr(youtube_playlist_item, "normalized_artist", ""),
                        str(getattr(youtube_playlist_item, "duration_seconds", None)),
                        self._serializeTimestamp(
                            getattr(youtube_playlist_item, "updated_at", None)
                            or getattr(youtube_playlist_item, "created_at", None)
                        ),
                    ]
                )
            )
        digest = hashlib.sha1("\n".join(serialized_items).encode("utf-8")).hexdigest()
        return f"youtube_playlist:{digest}"

    def _buildLocalLibraryStateFingerprint(self, local_songs: list[object]) -> str:
        serialized_songs = []
        for local_song in sorted(
            local_songs,
            key=lambda song: (
                getattr(song, "file_path", ""),
                getattr(song, "id", 0) or 0,
            ),
        ):
            serialized_songs.append(
                "|".join(
                    [
                        str(getattr(local_song, "id", None) or 0),
                        getattr(local_song, "file_path", ""),
                        getattr(local_song, "title", ""),
                        getattr(local_song, "artist", ""),
                        str(getattr(local_song, "duration_seconds", None)),
                        "1" if getattr(local_song, "is_available", False) else "0",
                        self._serializeTimestamp(
                            getattr(local_song, "updated_at", None)
                            or getattr(local_song, "created_at", None)
                        ),
                    ]
                )
            )
        digest = hashlib.sha1("\n".join(serialized_songs).encode("utf-8")).hexdigest()
        return f"local_library:{digest}"

    def _serializeTimestamp(self, timestamp: datetime | None) -> str:
        timestamp = self._normalizeTimestamp(timestamp)
        if timestamp is None:
            return "na"
        return timestamp.isoformat()

    def _normalizeTimestamp(self, timestamp: datetime | None) -> datetime | None:
        if timestamp is None:
            return None
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=UTC)
        return timestamp.astimezone(UTC)

    def _buildFrozenFoundReason(self, matched_by: str | None) -> str:
        if matched_by in {MANUAL_USER_LINKED_LOCAL_SONG, MANUAL_USER_MARKED_FOUND}:
            return "Coincidencia FOUND conservada desde snapshot manual valido."
        return "Coincidencia FOUND conservada desde snapshot automatico valido."

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
