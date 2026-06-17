from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlaylistComparisonPhaseTimingsDto:
    snapshot_load_seconds: float
    pool_build_seconds: float
    indexing_seconds: float
    matching_seconds: float
    persistence_seconds: float
    total_seconds: float
