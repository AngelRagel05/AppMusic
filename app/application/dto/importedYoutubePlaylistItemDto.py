from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ImportedYoutubePlaylistItemDto:
    external_video_id: str
    position: int
    raw_title: str
    raw_channel_name: str
    duration_seconds: float | None = None
    published_at: datetime | None = None
