from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.shared.constants.comparison import ComparisonStatus


def buildComparisonReasonSummary(
    comparison_item: PlaylistComparisonItemResultDto,
) -> str:
    normalized = comparison_item.reason.strip().rstrip(".")
    if normalized:
        return f"{normalized}."
    if comparison_item.comparison_status is ComparisonStatus.FOUND:
        return "Coincidencia validada."
    if comparison_item.comparison_status is ComparisonStatus.POSSIBLE_MATCH:
        return "Coincidencia posible pendiente de revision."
    return "No hay candidata suficientemente competitiva."
