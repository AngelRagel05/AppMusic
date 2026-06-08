from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonAvailabilitySummary import (
    buildComparisonAvailabilitySummary,
)
from app.shared.constants.comparison import ComparisonStatus


def test_build_comparison_availability_summary_marks_found_items_as_existing_locally() -> None:
    item = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=1,
        local_song_id=2,
        comparison_status=ComparisonStatus.FOUND,
        youtube_title="Song One",
        youtube_artist="Artist One",
        local_title="Song One",
        local_artist="Artist One",
        score=96.0,
        reason="Coincidencia fuerte.",
    )

    assert buildComparisonAvailabilitySummary(item) == "Existe en local"


def test_build_comparison_availability_summary_marks_possible_matches_as_possible_local_items() -> None:
    item = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=1,
        local_song_id=2,
        comparison_status=ComparisonStatus.POSSIBLE_MATCH,
        youtube_title="Song One Live",
        youtube_artist="Artist One",
        local_title="Song One",
        local_artist="Artist One feat Guest",
        score=76.0,
        reason="Coincidencia parcial.",
    )

    assert buildComparisonAvailabilitySummary(item) == (
        "Posible coincidencia dudosa en local | Revisar manualmente"
    )


def test_build_comparison_availability_summary_marks_missing_items_as_not_existing_locally() -> None:
    item = PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=1,
        local_song_id=None,
        comparison_status=ComparisonStatus.MISSING,
        youtube_title="Lost Tape",
        youtube_artist="Rare Crew",
        local_title=None,
        local_artist=None,
        score=0.0,
        reason="Sin coincidencia suficiente.",
    )

    assert buildComparisonAvailabilitySummary(item) == "No existe en local"
