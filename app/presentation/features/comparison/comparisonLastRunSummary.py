from __future__ import annotations

from calendar import monthrange
from datetime import UTC, datetime, timedelta, timezone

from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)


def buildComparisonLastRunSummary(
    comparison_history: list[PlaylistComparisonHistoryEntryDto],
) -> str:
    if not comparison_history:
        return "Ultima comparacion: todavia no ejecutada"

    latest_entry = comparison_history[0]
    return (
        "Ultima comparacion: "
        f"{formatComparisonHistoryTimestamp(latest_entry.compared_at)}"
    )


def formatComparisonHistoryTimestamp(value: datetime) -> str:
    timestamp = _toMadridTimestamp(value)
    return timestamp.strftime("%d/%m/%Y %H:%M")


def _toMadridTimestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value

    utc_timestamp = value.astimezone(UTC)
    offset_hours = 2 if _isMadridDstActive(utc_timestamp) else 1
    return utc_timestamp.astimezone(timezone(timedelta(hours=offset_hours)))


def _isMadridDstActive(utc_timestamp: datetime) -> bool:
    year = utc_timestamp.year
    dst_start = _lastSundayAtUtc(year, 3)
    dst_end = _lastSundayAtUtc(year, 10)
    return dst_start <= utc_timestamp < dst_end


def _lastSundayAtUtc(year: int, month: int) -> datetime:
    last_day = monthrange(year, month)[1]
    candidate = datetime(year, month, last_day, 1, 0, tzinfo=UTC)
    days_since_sunday = (candidate.weekday() + 1) % 7
    return candidate - timedelta(days=days_since_sunday)
