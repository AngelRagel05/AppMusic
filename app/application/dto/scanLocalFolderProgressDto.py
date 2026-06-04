from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanLocalFolderProgressDto:
    processed_song_count: int
    total_song_count: int
