from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComparableLocalSong:
    id: int
    title: str
    artist: str
    duration_seconds: float
    normalized_title: str = ""
    normalized_artist: str = ""
    is_available: bool = True
    is_reserved: bool = False

    @property
    def comparable_title(self) -> str:
        return self.normalized_title or self.title

    @property
    def comparable_artist(self) -> str:
        return self.normalized_artist or self.artist


@dataclass(frozen=True, slots=True)
class ComparableYoutubePlaylistItem:
    id: int
    normalized_title: str
    normalized_artist: str
    duration_seconds: float | None

    @property
    def comparable_title(self) -> str:
        return self.normalized_title

    @property
    def comparable_artist(self) -> str:
        return self.normalized_artist
