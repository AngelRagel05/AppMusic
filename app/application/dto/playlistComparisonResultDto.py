from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto


@dataclass(frozen=True, slots=True)
class PlaylistComparisonResultDto:
    summary: PlaylistComparisonSummaryDto
    items: list[PlaylistComparisonItemResultDto]
