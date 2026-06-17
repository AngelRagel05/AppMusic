from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonObservabilityDto import (
    PlaylistComparisonObservabilityDto,
)
from app.application.dto.playlistComparisonPhaseTimingsDto import (
    PlaylistComparisonPhaseTimingsDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.application.dto.playlistComparisonVolumeMetricsDto import (
    PlaylistComparisonVolumeMetricsDto,
)
from app.shared.constants.comparison import ComparisonStatus


def test_playlist_comparison_item_result_dto_stores_comparison_fields() -> None:
    result = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=10,
        local_song_id=4,
        comparison_status=ComparisonStatus.FOUND,
        youtube_title="Song One",
        youtube_artist="Artist One",
        local_title="Song One",
        local_artist="Artist One",
        score=98.5,
        reason="Coincidencia exacta en titulo y artista normalizados.",
    )

    assert result.youtube_playlist_item_id == 10
    assert result.local_song_id == 4
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score == 98.5


def test_playlist_comparison_summary_dto_stores_summary_counts() -> None:
    summary = PlaylistComparisonSummaryDto(
        found_count=8,
        missing_count=2,
        possible_match_count=1,
        total_compared=11,
    )

    assert summary.found_count == 8
    assert summary.missing_count == 2
    assert summary.possible_match_count == 1
    assert summary.total_compared == 11


def test_playlist_comparison_result_dto_can_carry_observability_metrics() -> None:
    result = PlaylistComparisonResultDto(
        summary=PlaylistComparisonSummaryDto(
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        ),
        items=[],
        observability=PlaylistComparisonObservabilityDto(
            phase_timings=PlaylistComparisonPhaseTimingsDto(
                snapshot_load_seconds=0.11,
                pool_build_seconds=0.05,
                indexing_seconds=0.03,
                matching_seconds=0.40,
                persistence_seconds=0.07,
                total_seconds=0.66,
            ),
            volume_metrics=PlaylistComparisonVolumeMetricsDto(
                skipped_found_count=4,
                reserved_local_song_count=4,
                recomputed_item_count=2,
                total_candidates_considered=3,
                average_candidates_per_recomputed_item=1.5,
            ),
        ),
    )

    assert result.observability is not None
    assert result.observability.phase_timings.total_seconds == 0.66
    assert result.observability.volume_metrics.skipped_found_count == 4
    assert result.observability.volume_metrics.average_candidates_per_recomputed_item == 1.5
