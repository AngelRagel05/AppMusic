from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.domain.playlists.services import isAutomaticMatchedBy, isManualMatchedBy
from app.shared.constants.comparison import ComparisonStatus


ALL_COMPARISON_FILTER = "all"
FOUND_COMPARISON_FILTER = "matched"
MISSING_COMPARISON_FILTER = "missing"
POSSIBLE_MATCH_COMPARISON_FILTER = "possible_match"
MANUAL_COMPARISON_FILTER = "manual"
AUTOMATIC_COMPARISON_FILTER = "automatic"
COMPARISON_FILTER_VALUES = (
    ALL_COMPARISON_FILTER,
    FOUND_COMPARISON_FILTER,
    MISSING_COMPARISON_FILTER,
    POSSIBLE_MATCH_COMPARISON_FILTER,
    MANUAL_COMPARISON_FILTER,
    AUTOMATIC_COMPARISON_FILTER,
)


def filterComparisonItemsByStatus(
    items: list[PlaylistComparisonItemResultDto],
    selected_filter: str,
) -> list[PlaylistComparisonItemResultDto]:
    if selected_filter == FOUND_COMPARISON_FILTER:
        return [
            item
            for item in items
            if item.comparison_status is ComparisonStatus.FOUND
        ]
    if selected_filter == MISSING_COMPARISON_FILTER:
        return [
            item
            for item in items
            if item.comparison_status is ComparisonStatus.MISSING
        ]
    if selected_filter == POSSIBLE_MATCH_COMPARISON_FILTER:
        return [
            item
            for item in items
            if item.comparison_status is ComparisonStatus.POSSIBLE_MATCH
        ]
    if selected_filter == MANUAL_COMPARISON_FILTER:
        return [item for item in items if _isManualComparisonItem(item)]
    if selected_filter == AUTOMATIC_COMPARISON_FILTER:
        return [item for item in items if _isAutomaticComparisonItem(item)]
    return sorted(
        items,
        key=lambda item: (
            _comparisonVisibilityPriority(item.comparison_status),
            item.youtube_playlist_item_id,
        ),
    )


def _comparisonVisibilityPriority(status: ComparisonStatus) -> int:
    return {
        ComparisonStatus.MISSING: 0,
        ComparisonStatus.POSSIBLE_MATCH: 1,
        ComparisonStatus.FOUND: 2,
    }[status]


def _isManualComparisonItem(item: PlaylistComparisonItemResultDto) -> bool:
    return isManualMatchedBy(item.matched_by)


def _isAutomaticComparisonItem(item: PlaylistComparisonItemResultDto) -> bool:
    if isManualMatchedBy(item.matched_by):
        return False
    if isAutomaticMatchedBy(item.matched_by):
        return True
    return True
