from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanResult:
    scanned_files: int
    imported_songs: int
    skipped_existing: int

