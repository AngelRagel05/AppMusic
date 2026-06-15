from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class PlaylistComparisonResult:
    id: int | None = None
    playlist_comparison_id: int = 0
    youtube_playlist_item_id: int = 0
    local_song_id: int | None = None
    match_status: str = ""
    score: float | None = None
    matched_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        status = ComparisonStatus(self.match_status)
        if status is ComparisonStatus.MISSING and self.local_song_id is not None:
            raise ValueError(
                "Un resultado missing no puede mantener una cancion local enlazada."
            )
        if status is ComparisonStatus.FOUND and self.local_song_id is None:
            raise ValueError(
                "Un resultado found requiere una cancion local enlazada."
            )
        if self.matched_by is None:
            return

        normalized_matched_by = self.matched_by.strip()
        if not normalized_matched_by:
            raise ValueError("matched_by no puede ser una cadena vacia.")
        if ":" in normalized_matched_by and not normalized_matched_by.startswith(
            ("auto:", "manual:")
        ):
            raise ValueError(
                "matched_by debe usar los prefijos controlados auto: o manual:."
            )
