from __future__ import annotations

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonTableRowViewData import (
    buildComparisonTableRowViewData,
)
from app.shared.constants.comparison import ComparisonStatus


def test_buildComparisonTableRowViewData_formats_missing_rows_for_the_results_table() -> None:
    row = buildComparisonTableRowViewData(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=1,
            local_song_id=None,
            comparison_status=ComparisonStatus.MISSING,
            youtube_title="Numb",
            youtube_artist="Linkin Park",
            local_title=None,
            local_artist=None,
            score=0.0,
            reason="No se encontro coincidencia suficiente en la biblioteca local.",
        )
    )

    assert row.status_label == "Falta"
    assert row.local_match == "Sin coincidencia local"
    assert row.score_label == "0.0%"
    assert row.review_note == "Pendiente de descargar o escanear"
    assert "No existe" in row.availability_summary


def test_buildComparisonTableRowViewData_formats_possible_matches_for_manual_review() -> None:
    row = buildComparisonTableRowViewData(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=2,
            local_song_id=4,
            comparison_status=ComparisonStatus.POSSIBLE_MATCH,
            youtube_title="In the End",
            youtube_artist="Linkin Park",
            local_title="In The End",
            local_artist="Linkin Park",
            score=82.5,
            reason="Coincidencia parcial tras normalizar titulo y artista.",
        )
    )

    assert row.status_label == "Posible"
    assert row.local_match == "In The End · Linkin Park"
    assert row.score_label == "82.5%"
    assert row.review_note == "Revisar manualmente"
    assert "Posible coincidencia dudosa" in row.availability_summary


def test_buildComparisonTableRowViewData_formats_found_matches_as_confirmed() -> None:
    row = buildComparisonTableRowViewData(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=3,
            local_song_id=7,
            comparison_status=ComparisonStatus.FOUND,
            youtube_title="Breaking the Habit",
            youtube_artist="Linkin Park",
            local_title="Breaking the Habit",
            local_artist="Linkin Park",
            score=98.4,
            reason="Coincidencia fuerte en titulo y artista normalizados.",
        )
    )

    assert row.status_label == "Encontrada"
    assert row.review_note == "Coincidencia confirmada"
    assert row.score_label == "98.4%"
    assert row.reason_summary
