from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
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
