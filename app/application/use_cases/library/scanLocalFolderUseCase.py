from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto
from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository


class LocalMusicScannerPort(Protocol):
    def scanMp3Files(self, folderPath: str) -> list[str]:
        ...


class LocalSongMetadataReaderPort(Protocol):
    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        ...


class ScanLocalFolderUseCase:
    def __init__(
        self,
        local_folder_repository: LocalFolderRepository,
        local_song_repository: LocalSongRepository,
        local_music_scanner: LocalMusicScannerPort,
        local_song_metadata_reader: LocalSongMetadataReaderPort,
    ) -> None:
        self._local_folder_repository = local_folder_repository
        self._local_song_repository = local_song_repository
        self._local_music_scanner = local_music_scanner
        self._local_song_metadata_reader = local_song_metadata_reader

    def execute(self) -> ScanLocalFolderResultDto:
        activeLocalFolder = self._local_folder_repository.get_active()
        if activeLocalFolder is None or activeLocalFolder.id is None:
            raise ValueError("No hay una biblioteca local activa para escanear.")

        discoveredFilePaths = self._local_music_scanner.scanMp3Files(activeLocalFolder.path)
        createdSongCount = 0
        existingSongCount = 0

        for filePath in discoveredFilePaths:
            existingSong = self._local_song_repository.get_by_file_path(filePath)
            if existingSong is not None:
                existingSongCount += 1
                continue

            metadata = self._local_song_metadata_reader.readMetadata(filePath)
            self._local_song_repository.save(
                LocalSong(
                    local_folder_id=activeLocalFolder.id,
                    file_path=filePath,
                    file_name=Path(filePath).name,
                    title=metadata.title,
                    artist=metadata.artist,
                    album=metadata.album,
                    release_year=metadata.release_year,
                    track_number_album=metadata.track_number_album,
                    duration_seconds=metadata.duration_seconds,
                )
            )
            createdSongCount += 1

        return ScanLocalFolderResultDto(
            local_folder_id=activeLocalFolder.id,
            local_folder_name=activeLocalFolder.display_name,
            scanned_file_count=len(discoveredFilePaths),
            created_song_count=createdSongCount,
            existing_song_count=existingSongCount,
        )
