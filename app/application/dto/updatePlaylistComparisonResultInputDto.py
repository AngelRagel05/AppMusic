from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdatePlaylistComparisonResultInputDto:
    playlist_comparison_id: int
    youtube_playlist_item_id: int
    match_status: str
    local_song_id: int | None
