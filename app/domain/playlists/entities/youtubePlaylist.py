from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class YoutubePlaylist:
    id: int | None
    playlist_url: str
    external_playlist_id: str
    title: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
