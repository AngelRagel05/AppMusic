from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonResultDetailViewData import (
    buildComparisonResultDetailViewData,
)
from app.shared.constants.comparison import ComparisonStatus


def test_buildComparisonResultDetailViewData_returns_full_detail_for_linked_song() -> None:
    view_data = buildComparisonResultDetailViewData(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=1,
            local_song_id=8,
            comparison_status=ComparisonStatus.FOUND,
            youtube_title="Numb",
            youtube_artist="Linkin Park",
            local_title="Numb",
            local_artist="Linkin Park",
            score=98.2,
            reason="Titulo exacto con artista fuerte y duracion razonable.",
        ),
        LocalSongDto(
            id=8,
            local_folder_id=2,
            file_path=r"C:\Music\Linkin Park\Numb.mp3",
            file_name="Numb.mp3",
            is_available=True,
            title="Numb",
            artist="Linkin Park",
            album="Meteora",
            release_year=2003,
            track_number_album=13,
            duration_seconds=185.0,
        ),
    )

    assert view_data.title == "Numb"
    assert view_data.subtitle == "Linkin Park"
    assert view_data.status_label == "Encontrada"
    assert view_data.local_match == "Numb · Linkin Park"
    assert view_data.score_label == "98.2%"
    assert view_data.review_note == "Coincidencia confirmada"
    assert "Cancion local enlazada: Numb · Linkin Park" == view_data.linked_song_title
    assert "Titulo exacto con artista fuerte" in view_data.reason_summary


def test_buildComparisonResultDetailViewData_reports_missing_linked_song_when_absent() -> None:
    view_data = buildComparisonResultDetailViewData(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=2,
            local_song_id=None,
            comparison_status=ComparisonStatus.MISSING,
            youtube_title="Lost Tape",
            youtube_artist="Rare Crew",
            local_title=None,
            local_artist=None,
            score=0.0,
            reason="Duracion fuera de tolerancia fuerte.",
        ),
        None,
    )

    assert view_data.status_label == "Falta"
    assert view_data.local_match == "Sin coincidencia local"
    assert view_data.review_note == "Pendiente de descargar o escanear"
    assert view_data.linked_song_title == "Cancion local enlazada: no disponible"
    assert "no tiene una cancion local enlazada" in view_data.linked_song_detail
