from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


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
