from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mutagen import File


@dataclass(frozen=True, slots=True)
class SongMetadata:
    title: str | None
    artist: str | None
    album: str | None
    year: int | None
    track_number: int | None
    duration: float | None


class MetadataReader:
    def read(self, file_path: Path) -> SongMetadata:
        parsed_file = File(file_path)

        if parsed_file is None:
            return SongMetadata(None, None, None, None, None, None)

        tags = parsed_file.tags or {}
        info = getattr(parsed_file, "info", None)

        return SongMetadata(
            title=self._first_tag(tags, ("TIT2", "title")),
            artist=self._first_tag(tags, ("TPE1", "artist")),
            album=self._first_tag(tags, ("TALB", "album")),
            year=self._safe_int(self._first_tag(tags, ("TDRC", "date", "year"))),
            track_number=self._safe_int(self._first_tag(tags, ("TRCK", "tracknumber"))),
            duration=getattr(info, "length", None),
        )

    @staticmethod
    def _first_tag(tags: object, keys: tuple[str, ...]) -> str | None:
        for key in keys:
            if key not in tags:
                continue

            raw_value = tags[key]

            if isinstance(raw_value, list) and raw_value:
                return str(raw_value[0]).strip()

            text = getattr(raw_value, "text", None)
            if isinstance(text, list) and text:
                return str(text[0]).strip()

            return str(raw_value).strip()

        return None

    @staticmethod
    def _safe_int(value: str | None) -> int | None:
        if not value:
            return None

        numeric = value.split("/")[0].strip()
        return int(numeric) if numeric.isdigit() else None

