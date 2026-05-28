from __future__ import annotations

from pathlib import Path

from loguru import logger

from music_app.app.application.dto.scan_result import ScanResult
from music_app.app.domain.entities.song import Song
from music_app.app.domain.services.song_repository import SongRepository
from music_app.app.infrastructure.filesystem.music_scanner import MusicScanner
from music_app.app.infrastructure.metadata.reader import MetadataReader


class ScanMusicFolderUseCase:
    def __init__(
        self,
        *,
        song_repository: SongRepository,
        music_scanner: MusicScanner,
        metadata_reader: MetadataReader,
    ) -> None:
        self._song_repository = song_repository
        self._music_scanner = music_scanner
        self._metadata_reader = metadata_reader

    def execute(self, folder_path: str) -> ScanResult:
        root_path = Path(folder_path).expanduser().resolve()
        scanned_files = 0
        imported_songs = 0
        skipped_existing = 0

        logger.info("Scanning music folder: {}", root_path)

        for audio_file in self._music_scanner.scan(root_path):
            scanned_files += 1
            normalized_path = str(audio_file)

            if self._song_repository.get_by_path(normalized_path):
                skipped_existing += 1
                continue

            metadata = self._metadata_reader.read(audio_file)
            song = Song.new(
                path=normalized_path,
                title=metadata.title or audio_file.stem,
                artist=metadata.artist or "",
                album=metadata.album or "",
                year=metadata.year,
                track_number=metadata.track_number,
                duration=metadata.duration,
            )
            self._song_repository.add(song)
            imported_songs += 1

        return ScanResult(
            scanned_files=scanned_files,
            imported_songs=imported_songs,
            skipped_existing=skipped_existing,
        )

