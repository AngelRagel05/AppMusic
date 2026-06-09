from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonLinkedLocalSongSummary import (
    buildComparisonLinkedLocalSongSummary,
)
from app.shared.constants.comparison import ComparisonStatus


def test_buildComparisonLinkedLocalSongSummary_returns_linked_song_detail_when_song_exists() -> None:
    summary = buildComparisonLinkedLocalSongSummary(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=1,
            local_song_id=7,
            comparison_status=ComparisonStatus.FOUND,
            youtube_title="Numb",
            youtube_artist="Linkin Park",
            local_title="Numb",
            local_artist="Linkin Park",
            score=98.0,
            reason="Coincidencia fuerte.",
        ),
        LocalSongDto(
            id=7,
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

    assert summary.title == "Cancion local enlazada: Numb · Linkin Park"
    assert "Archivo: Numb.mp3" in summary.detail
    assert "Album: Meteora" in summary.detail
    assert r"Ruta: C:\Music\Linkin Park\Numb.mp3" in summary.detail


def test_buildComparisonLinkedLocalSongSummary_returns_unavailable_message_when_song_is_missing() -> None:
    summary = buildComparisonLinkedLocalSongSummary(
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=2,
            local_song_id=None,
            comparison_status=ComparisonStatus.MISSING,
            youtube_title="Lost Track",
            youtube_artist="Unknown Artist",
            local_title=None,
            local_artist=None,
            score=0.0,
            reason="No se encontro coincidencia.",
        ),
        None,
    )

    assert summary.title == "Cancion local enlazada: no disponible"
    assert "no tiene una cancion local enlazada" in summary.detail
