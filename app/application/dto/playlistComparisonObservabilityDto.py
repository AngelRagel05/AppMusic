from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.playlistComparisonPhaseTimingsDto import (
    PlaylistComparisonPhaseTimingsDto,
)
from app.application.dto.playlistComparisonVolumeMetricsDto import (
    PlaylistComparisonVolumeMetricsDto,
)


@dataclass(frozen=True, slots=True)
class PlaylistComparisonObservabilityDto:
    phase_timings: PlaylistComparisonPhaseTimingsDto
    volume_metrics: PlaylistComparisonVolumeMetricsDto
