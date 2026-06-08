from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PlaylistComparisonHistoryEntryDto:
    comparison_id: int
    compared_at: datetime
    found_count: int
    missing_count: int
    possible_match_count: int
    total_compared: int
