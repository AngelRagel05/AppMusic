from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonReasonSummary import (
    buildComparisonReasonSummary,
)
from app.shared.constants.comparison import ComparisonStatus


def test_build_comparison_reason_summary_returns_readable_found_explanation() -> None:
    item = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=1,
        local_song_id=2,
        comparison_status=ComparisonStatus.FOUND,
        youtube_title="Song One",
        youtube_artist="Artist One",
        local_title="Song One",
        local_artist="Artist One",
        score=96.0,
        reason="Titulo exacto con artista fuerte y duracion razonable.",
    )

    assert (
        buildComparisonReasonSummary(item)
        == "Titulo exacto con artista fuerte y duracion razonable."
    )


def test_build_comparison_reason_summary_returns_readable_possible_match_explanation() -> None:
    item = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=1,
        local_song_id=2,
        comparison_status=ComparisonStatus.POSSIBLE_MATCH,
        youtube_title="Song One Live",
        youtube_artist="Artist One",
        local_title="Song One",
        local_artist="Artist One feat Guest",
        score=76.0,
        reason="Ambiguedad entre dos candidatas plausibles.",
    )

    assert buildComparisonReasonSummary(item) == "Ambiguedad entre dos candidatas plausibles."


def test_build_comparison_reason_summary_returns_readable_missing_explanation() -> None:
    item = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=1,
        local_song_id=None,
        comparison_status=ComparisonStatus.MISSING,
        youtube_title="Lost Tape",
        youtube_artist="Rare Crew",
        local_title=None,
        local_artist=None,
        score=0.0,
        reason="Duracion fuera de tolerancia fuerte.",
    )

    assert buildComparisonReasonSummary(item) == "Duracion fuera de tolerancia fuerte."
