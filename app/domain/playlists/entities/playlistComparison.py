from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PlaylistComparison:
    id: int | None = None
    youtube_playlist_id: int = 0
    local_folder_id: int = 0
    compared_at: datetime | None = None
    created_at: datetime | None = None
