from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlaylistComparisonVolumeMetricsDto:
    skipped_found_count: int
    reserved_local_song_count: int
    recomputed_item_count: int
    total_candidates_considered: int
    average_candidates_per_recomputed_item: float
