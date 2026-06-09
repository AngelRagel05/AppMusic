from __future__ import annotations

from datetime import datetime

from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)


def buildComparisonLastRunSummary(
    comparison_history: list[PlaylistComparisonHistoryEntryDto],
) -> str:
    if not comparison_history:
        return "Ultima comparacion: todavia no ejecutada"

    latest_entry = comparison_history[0]
    return f"Ultima comparacion: {_formatHistoryTimestamp(latest_entry.compared_at)}"


def _formatHistoryTimestamp(value: datetime) -> str:
    timestamp = value.astimezone() if value.tzinfo is not None else value
    return timestamp.strftime("%d/%m/%Y %H:%M")
