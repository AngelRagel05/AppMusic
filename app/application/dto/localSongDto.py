from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalSongDto:
    id: int
    local_folder_id: int
    file_path: str
    file_name: str
    is_available: bool
    title: str
    artist: str
    album: str
    release_year: int
    track_number_album: int
    duration_seconds: float
