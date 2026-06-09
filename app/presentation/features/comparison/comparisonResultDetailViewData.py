from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonAvailabilitySummary import (
    buildComparisonAvailabilitySummary,
)
from app.presentation.features.comparison.comparisonLinkedLocalSongSummary import (
    buildComparisonLinkedLocalSongSummary,
)
from app.presentation.features.comparison.comparisonReasonSummary import (
    buildComparisonReasonSummary,
)
from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class ComparisonResultDetailViewData:
    title: str
    subtitle: str
    status_label: str
    score_label: str
    availability_summary: str
    linked_song_title: str
    linked_song_detail: str
    reason_summary: str
    raw_reason: str


def buildComparisonResultDetailViewData(
    comparison_item: PlaylistComparisonItemResultDto,
    linked_local_song: LocalSongDto | None,
) -> ComparisonResultDetailViewData:
    linked_song_summary = buildComparisonLinkedLocalSongSummary(
        comparison_item,
        linked_local_song,
    )
    return ComparisonResultDetailViewData(
        title=comparison_item.youtube_title,
        subtitle=comparison_item.youtube_artist,
        status_label=_buildStatusLabel(comparison_item.comparison_status),
        score_label=f"{comparison_item.score:.1f}%",
        availability_summary=buildComparisonAvailabilitySummary(comparison_item),
        linked_song_title=linked_song_summary.title,
        linked_song_detail=linked_song_summary.detail,
        reason_summary=buildComparisonReasonSummary(comparison_item),
        raw_reason=comparison_item.reason,
    )


def _buildStatusLabel(status: ComparisonStatus) -> str:
    return {
        ComparisonStatus.FOUND: "Encontrada",
        ComparisonStatus.MISSING: "Falta",
        ComparisonStatus.POSSIBLE_MATCH: "Posible coincidencia",
    }[status]
