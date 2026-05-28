from __future__ import annotations

from pathlib import Path


class MusicScanner:
    SUPPORTED_EXTENSIONS = {".mp3"}

    def scan(self, root_path: Path) -> list[Path]:
        return sorted(
            path
            for path in root_path.rglob("*")
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS
        )

