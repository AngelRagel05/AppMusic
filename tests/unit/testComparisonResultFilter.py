from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    ALL_COMPARISON_FILTER,
    AUTOMATIC_COMPARISON_FILTER,
    FOUND_COMPARISON_FILTER,
    MANUAL_COMPARISON_FILTER,
    MISSING_COMPARISON_FILTER,
    POSSIBLE_MATCH_COMPARISON_FILTER,
    filterComparisonItemsByStatus,
)
from app.shared.constants.comparison import ComparisonStatus


def _build_item(
    comparison_status: ComparisonStatus,
    youtube_playlist_item_id: int,
    *,
    matched_by: str | None = None,
):
    return PlaylistComparisonItemResultDto(
        youtube_playlist_item_id=youtube_playlist_item_id,
        local_song_id=None,
        comparison_status=comparison_status,
        youtube_title=f"Song {youtube_playlist_item_id}",
        youtube_artist="Artist",
        local_title=None,
        local_artist=None,
        score=0.0,
        reason="reason",
        matched_by=matched_by,
    )


def test_filter_comparison_items_by_status_returns_all_items() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1),
        _build_item(ComparisonStatus.MISSING, 2),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3),
    ]

    filtered_items = filterComparisonItemsByStatus(items, ALL_COMPARISON_FILTER)

    assert filtered_items == [items[1], items[2], items[0]]


def test_filter_comparison_items_by_status_prioritizes_missing_items_in_all_view() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 5),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 2),
        _build_item(ComparisonStatus.MISSING, 9),
        _build_item(ComparisonStatus.MISSING, 1),
    ]

    filtered_items = filterComparisonItemsByStatus(items, ALL_COMPARISON_FILTER)

    assert [item.youtube_playlist_item_id for item in filtered_items] == [1, 9, 2, 5]


def test_filter_comparison_items_by_status_returns_only_found_items() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1),
        _build_item(ComparisonStatus.MISSING, 2),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3),
    ]

    filtered_items = filterComparisonItemsByStatus(items, FOUND_COMPARISON_FILTER)

    assert filtered_items == [items[0]]


def test_filter_comparison_items_by_status_returns_only_missing_items() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1),
        _build_item(ComparisonStatus.MISSING, 2),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3),
    ]

    filtered_items = filterComparisonItemsByStatus(items, MISSING_COMPARISON_FILTER)

    assert filtered_items == [items[1]]


def test_filter_comparison_items_by_status_returns_only_possible_matches() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1),
        _build_item(ComparisonStatus.MISSING, 2),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3),
    ]

    filtered_items = filterComparisonItemsByStatus(items, POSSIBLE_MATCH_COMPARISON_FILTER)

    assert filtered_items == [items[2]]


def test_filter_comparison_items_by_status_returns_only_manual_items() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1, matched_by="auto:title_artist_duration"),
        _build_item(ComparisonStatus.MISSING, 2, matched_by="manual:user_marked_missing"),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3, matched_by="manual:user_marked_possible"),
    ]

    filtered_items = filterComparisonItemsByStatus(items, MANUAL_COMPARISON_FILTER)

    assert filtered_items == [items[1], items[2]]


def test_filter_comparison_items_by_status_returns_automatic_items_and_legacy_rows() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1, matched_by="auto:title_artist_duration"),
        _build_item(
            ComparisonStatus.MISSING,
            2,
            matched_by="Titulo exacto con artista fuerte y duracion razonable.",
        ),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3, matched_by="manual:user_marked_possible"),
    ]

    filtered_items = filterComparisonItemsByStatus(items, AUTOMATIC_COMPARISON_FILTER)

    assert filtered_items == [items[0], items[1]]


def test_comparison_filter_values_expose_stable_requested_keys() -> None:
    from app.presentation.features.comparison.comparisonResultFilter import (
        COMPARISON_FILTER_VALUES,
    )

    assert COMPARISON_FILTER_VALUES == (
        "all",
        "matched",
        "missing",
        "possible_match",
        "manual",
        "automatic",
    )
