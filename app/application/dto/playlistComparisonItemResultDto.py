from __future__ import annotations

from dataclasses import dataclass

from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class PlaylistComparisonItemResultDto:
    youtube_playlist_item_id: int
    local_song_id: int | None
    comparison_status: ComparisonStatus
    youtube_title: str
    youtube_artist: str
    local_title: str | None
    local_artist: str | None
    score: float
    reason: str
    matched_by: str | None = None
