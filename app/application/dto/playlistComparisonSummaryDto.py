from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlaylistComparisonSummaryDto:
    found_count: int
    missing_count: int
    possible_match_count: int
    total_compared: int
