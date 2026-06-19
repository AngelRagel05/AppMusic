from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LocalSong:
    id: int | None = None
    local_folder_id: int | None = None
    download_id: int | None = None
    file_path: str = ""
    file_name: str = ""
    is_available: bool = True
    title: str = ""
    artist: str = ""
    normalized_title: str = ""
    normalized_artist: str = ""
    album: str = ""
    release_year: int = 0
    track_number_album: int = 0
    duration_seconds: float = 0.0
    created_at: datetime | None = None
    updated_at: datetime | None = None
