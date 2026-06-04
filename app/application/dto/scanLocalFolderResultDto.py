from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanLocalFolderResultDto:
    local_folder_id: int
    local_folder_name: str
    scanned_file_count: int
    created_song_count: int
    existing_song_count: int
    updated_song_count: int = 0
    missing_song_count: int = 0
    moved_song_count: int = 0
