from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalSongMetadataDto:
    title: str
    artist: str
    album: str
    release_year: int
    track_number_album: int
    duration_seconds: float
