from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)


@dataclass(frozen=True, slots=True)
class ComparisonLinkedLocalSongSummary:
    title: str
    detail: str


def buildComparisonLinkedLocalSongSummary(
    comparison_item: PlaylistComparisonItemResultDto,
    linked_local_song: LocalSongDto | None,
) -> ComparisonLinkedLocalSongSummary:
    if linked_local_song is None:
        return ComparisonLinkedLocalSongSummary(
            title="Cancion local enlazada: no disponible",
            detail="Este resultado no tiene una cancion local enlazada cargada en la vista actual.",
        )

    artist = linked_local_song.artist or "Artista desconocido"
    album = linked_local_song.album or "Album sin informar"
    title = linked_local_song.title or linked_local_song.file_name
    return ComparisonLinkedLocalSongSummary(
        title=f"Cancion local enlazada: {title} · {artist}",
        detail=(
            f"Archivo: {linked_local_song.file_name} | "
            f"Album: {album} | "
            f"Ruta: {linked_local_song.file_path}"
        ),
    )
