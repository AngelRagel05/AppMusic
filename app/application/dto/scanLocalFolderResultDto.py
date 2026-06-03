from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanLocalFolderResultDto:
    local_folder_id: int
    local_folder_name: str
    scanned_file_count: int
    created_song_count: int
    existing_song_count: int
