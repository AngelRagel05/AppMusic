from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonObservabilityDto import (
    PlaylistComparisonObservabilityDto,
)
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto


@dataclass(frozen=True, slots=True)
class PlaylistComparisonResultDto:
    summary: PlaylistComparisonSummaryDto
    items: list[PlaylistComparisonItemResultDto]
    playlist_comparison_id: int | None = None
    last_compared_at: datetime | None = None
    observability: PlaylistComparisonObservabilityDto | None = None
