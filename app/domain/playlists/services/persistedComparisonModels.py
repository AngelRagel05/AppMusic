from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComparableLocalSong:
    id: int
    title: str
    artist: str
    duration_seconds: float
    normalized_title: str = ""
    normalized_artist_full: str = ""
    normalized_artist_primary: str = ""
    normalized_artist_collaborators: tuple[str, ...] = ()
    is_available: bool = True
    is_reserved: bool = False

    @property
    def comparable_title(self) -> str:
        return self.normalized_title or self.title

    @property
    def comparable_artist_full(self) -> str:
        return self.normalized_artist_full or self.artist

    @property
    def comparable_artist_primary(self) -> str:
        return self.normalized_artist_primary or self.comparable_artist_full

    @property
    def comparable_artist_collaborators(self) -> tuple[str, ...]:
        return self.normalized_artist_collaborators


@dataclass(frozen=True, slots=True)
class ComparableYoutubePlaylistItem:
    id: int
    normalized_title: str
    normalized_artist_full: str
    duration_seconds: float | None
    normalized_artist_primary: str = ""
    normalized_artist_collaborators: tuple[str, ...] = ()

    @property
    def comparable_title(self) -> str:
        return self.normalized_title

    @property
    def comparable_artist_full(self) -> str:
        return self.normalized_artist_full

    @property
    def comparable_artist_primary(self) -> str:
        return self.normalized_artist_primary or self.normalized_artist_full

    @property
    def comparable_artist_collaborators(self) -> tuple[str, ...]:
        return self.normalized_artist_collaborators
