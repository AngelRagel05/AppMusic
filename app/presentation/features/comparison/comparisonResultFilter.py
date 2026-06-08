from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.shared.constants.comparison import ComparisonStatus


ALL_COMPARISON_FILTER = "Todos"
FOUND_COMPARISON_FILTER = "Encontradas"
MISSING_COMPARISON_FILTER = "Faltan"
POSSIBLE_MATCH_COMPARISON_FILTER = "Posibles coincidencias"
COMPARISON_FILTER_VALUES = (
    ALL_COMPARISON_FILTER,
    FOUND_COMPARISON_FILTER,
    MISSING_COMPARISON_FILTER,
    POSSIBLE_MATCH_COMPARISON_FILTER,
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
