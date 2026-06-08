from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.shared.constants.comparison import ComparisonStatus


def buildComparisonAvailabilitySummary(
    comparison_item: PlaylistComparisonItemResultDto,
) -> str:
    if comparison_item.comparison_status is ComparisonStatus.FOUND:
        return "Existe en local"
    if comparison_item.comparison_status is ComparisonStatus.POSSIBLE_MATCH:
        return "Posible coincidencia dudosa en local | Revisar manualmente"
    return "No existe en local"
