from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonAvailabilitySummary import (
    buildComparisonAvailabilitySummary,
)
from app.presentation.features.comparison.comparisonReasonSummary import (
    buildComparisonReasonSummary,
)
from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class ComparisonTableRowViewData:
    status_label: str
    playlist_title: str
    playlist_artist: str
    local_match: str
    score_label: str
    review_note: str
    availability_summary: str
    reason_summary: str


def buildComparisonTableRowViewData(
    comparison_item: PlaylistComparisonItemResultDto,
) -> ComparisonTableRowViewData:
    return ComparisonTableRowViewData(
        status_label=_buildStatusLabel(comparison_item.comparison_status),
        playlist_title=comparison_item.youtube_title,
        playlist_artist=comparison_item.youtube_artist,
        local_match=_buildLocalMatchLabel(comparison_item),
        score_label=f"{comparison_item.score:.1f}%",
        review_note=_buildReviewNote(comparison_item.comparison_status),
        availability_summary=buildComparisonAvailabilitySummary(comparison_item),
        reason_summary=buildComparisonReasonSummary(comparison_item),
    )


def _buildStatusLabel(status: ComparisonStatus) -> str:
    return {
        ComparisonStatus.FOUND: "Encontrada",
        ComparisonStatus.MISSING: "Falta",
        ComparisonStatus.POSSIBLE_MATCH: "Posible",
    }[status]


def _buildLocalMatchLabel(comparison_item: PlaylistComparisonItemResultDto) -> str:
    if comparison_item.local_title and comparison_item.local_artist:
        return f"{comparison_item.local_title} · {comparison_item.local_artist}"
    if comparison_item.local_title:
        return comparison_item.local_title
    if comparison_item.comparison_status is ComparisonStatus.MISSING:
        return "Sin coincidencia local"
    return "Coincidencia sin metadata completa"


def _buildReviewNote(status: ComparisonStatus) -> str:
    return {
        ComparisonStatus.FOUND: "Coincidencia confirmada",
        ComparisonStatus.MISSING: "Pendiente de descargar o escanear",
        ComparisonStatus.POSSIBLE_MATCH: "Revisar manualmente",
    }[status]
