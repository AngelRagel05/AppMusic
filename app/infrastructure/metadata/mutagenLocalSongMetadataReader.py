from __future__ import annotations

from pathlib import Path

from mutagen import File as MutagenFile
from mutagen import MutagenError
from mutagen.mp3 import MP3

from app.application.dto.localSongMetadataDto import LocalSongMetadataDto


class MutagenLocalSongMetadataReader:
    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        path = Path(filePath)
        fallbackTitle = path.stem

        try:
            audioFile = MutagenFile(filePath, easy=True)
            mp3File = MP3(filePath)
        except (MutagenError, OSError):
            return LocalSongMetadataDto(
                title=fallbackTitle,
                artist="",
                album="",
                release_year=0,
                track_number_album=0,
                duration_seconds=0.0,
            )

        title = self._firstValue(audioFile, "title") or fallbackTitle
        artist = self._firstValue(audioFile, "artist")
        album = self._firstValue(audioFile, "album")
        releaseYear = self._parseYear(
            self._firstValue(audioFile, "date") or self._firstValue(audioFile, "originaldate")
        )
        trackNumberAlbum = self._parseTrackNumber(self._firstValue(audioFile, "tracknumber"))
        durationSeconds = float(getattr(getattr(mp3File, "info", None), "length", 0.0) or 0.0)

        return LocalSongMetadataDto(
            title=title,
            artist=artist,
            album=album,
            release_year=releaseYear,
            track_number_album=trackNumberAlbum,
            duration_seconds=durationSeconds,
        )

    def _firstValue(self, audioFile, key: str) -> str:
        if audioFile is None:
            return ""
        values = audioFile.get(key, [])
        if not values:
            return ""
        value = str(values[0]).strip()
        return value

    def _parseYear(self, value: str) -> int:
        if not value:
            return 0
        digits = "".join(character for character in value if character.isdigit())
        if len(digits) < 4:
            return 0
        return int(digits[:4])

    def _parseTrackNumber(self, value: str) -> int:
        if not value:
            return 0
        prefix = value.split("/", maxsplit=1)[0].strip()
        return int(prefix) if prefix.isdigit() else 0
