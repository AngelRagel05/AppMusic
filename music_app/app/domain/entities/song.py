from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class Song:
    id: int | None
    path: str
    title: str
    artist: str
    album: str
    year: int | None
    track_number: int | None
    duration: float | None
    created_at: datetime

    @classmethod
    def new(
        cls,
        *,
        path: str,
        title: str,
        artist: str = "",
        album: str = "",
        year: int | None = None,
        track_number: int | None = None,
        duration: float | None = None,
    ) -> "Song":
        return cls(
            id=None,
            path=path,
            title=title,
            artist=artist,
            album=album,
            year=year,
            track_number=track_number,
            duration=duration,
            created_at=datetime.now(UTC),
        )

