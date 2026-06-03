from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class YoutubePlaylistDto:
    id: int
    playlist_url: str
    external_playlist_id: str
    title: str
    is_active: bool
