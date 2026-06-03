from __future__ import annotations

from pathlib import Path


def normalizeLocalSongFilePath(file_path: str) -> str:
    return str(Path(file_path).expanduser().resolve())
