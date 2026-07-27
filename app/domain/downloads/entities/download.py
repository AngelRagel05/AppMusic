from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Download:
    id: int | None
    youtube_playlist_item_id: int | None
    local_folder_id: int
    task_id: str
    source_url: str
    source_title: str | None
    source_artist: str | None
    status: str
    progress_percent: float
    target_file_path: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
