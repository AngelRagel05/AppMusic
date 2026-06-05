from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.shared.constants.comparison import ComparisonStatus


def buildComparisonReasonSummary(
    comparison_item: PlaylistComparisonItemResultDto,
) -> str:
    if comparison_item.comparison_status is ComparisonStatus.FOUND:
        return _normalizeFoundReason(comparison_item.reason)
    if comparison_item.comparison_status is ComparisonStatus.POSSIBLE_MATCH:
        return _normalizePossibleMatchReason(comparison_item.reason)
    return "Sin coincidencia suficiente."


def _normalizeFoundReason(reason: str) -> str:
    normalized = reason.strip().rstrip(".")
    if not normalized:
        return "Coincidencia valida."
    normalized = normalized.replace("Coincidencia ponderada fuerte", "Valida")
    normalized = normalized.replace("titulo", "titulo")
    normalized = normalized.replace("artista", "artista")
    return f"{normalized}."


def _normalizePossibleMatchReason(reason: str) -> str:
    normalized = reason.strip().rstrip(".")
    if not normalized:
        return "Coincidencia parcial."
    normalized = normalized.replace("Coincidencia parcial detectada", "Parcial")
    return f"{normalized}."
