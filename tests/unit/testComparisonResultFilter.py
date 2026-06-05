from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    ALL_COMPARISON_FILTER,
    FOUND_COMPARISON_FILTER,
    MISSING_COMPARISON_FILTER,
    POSSIBLE_MATCH_COMPARISON_FILTER,
    filterComparisonItemsByStatus,
)
from app.shared.constants.comparison import ComparisonStatus


def _build_item(comparison_status: ComparisonStatus, youtube_playlist_item_id: int):
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
    )


def test_filter_comparison_items_by_status_returns_all_items() -> None:
    items = [
        _build_item(ComparisonStatus.FOUND, 1),
        _build_item(ComparisonStatus.MISSING, 2),
        _build_item(ComparisonStatus.POSSIBLE_MATCH, 3),
    ]

    filtered_items = filterComparisonItemsByStatus(items, ALL_COMPARISON_FILTER)

    assert filtered_items == items


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
