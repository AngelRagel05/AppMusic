from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComparableLocalSong:
    id: int
    title: str
    artist: str
    duration_seconds: float
    is_available: bool = True
    is_reserved: bool = False


@dataclass(frozen=True, slots=True)
class ComparableYoutubePlaylistItem:
    id: int
    normalized_title: str
    normalized_artist: str
    duration_seconds: float | None
