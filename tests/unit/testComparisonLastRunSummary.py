from __future__ import annotations

from datetime import UTC, datetime

from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.presentation.features.comparison.comparisonLastRunSummary import (
    buildComparisonLastRunSummary,
)


def test_buildComparisonLastRunSummary_returns_pending_message_without_history() -> None:
    assert buildComparisonLastRunSummary([]) == "Ultima comparacion: todavia no ejecutada"


def test_buildComparisonLastRunSummary_returns_latest_execution_timestamp() -> None:
    history = [
        PlaylistComparisonHistoryEntryDto(
            comparison_id=12,
            compared_at=datetime(2026, 6, 9, 10, 45, tzinfo=UTC),
            found_count=10,
            missing_count=2,
            possible_match_count=1,
            total_compared=13,
        ),
        PlaylistComparisonHistoryEntryDto(
            comparison_id=8,
            compared_at=datetime(2026, 6, 8, 20, 15, tzinfo=UTC),
            found_count=8,
            missing_count=1,
            possible_match_count=0,
            total_compared=9,
        ),
    ]

    assert buildComparisonLastRunSummary(history) == "Ultima comparacion: 09/06/2026 12:45"
