from __future__ import annotations

from mutagen import File as MutagenFile
from mutagen import MutagenError

from app.application.dto.localSongMetadataUpdateDto import LocalSongMetadataUpdateDto


class MutagenLocalSongMetadataWriter:
    def writeMetadata(
        self,
        filePath: str,
        metadata: LocalSongMetadataUpdateDto,
    ) -> None:
        try:
            audio_file = MutagenFile(filePath, easy=True)
            if audio_file is None:
                raise ValueError("El archivo no es un MP3 compatible.")
            if audio_file.tags is None:
                audio_file.add_tags()

            audio_file["title"] = [metadata.title]
            audio_file["artist"] = [metadata.artist]
            audio_file["album"] = [metadata.album]
            self._setOptionalTag(
                audio_file,
                "date",
                str(metadata.release_year) if metadata.release_year else "",
            )
            self._setOptionalTag(
                audio_file,
                "tracknumber",
                str(metadata.track_number_album)
                if metadata.track_number_album
                else "",
            )
            audio_file.save()
        except (MutagenError, OSError) as error:
            raise ValueError(
                f"No se pudo escribir la metadata del MP3: {error}"
            ) from error

    def _setOptionalTag(self, audio_file, key: str, value: str) -> None:
        if value:
            audio_file[key] = [value]
            return
        if key in audio_file:
            del audio_file[key]
