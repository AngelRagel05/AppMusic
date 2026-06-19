from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import PureWindowsPath
from typing import Protocol

from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.dto.scanLocalFolderProgressDto import ScanLocalFolderProgressDto
from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto
from app.domain.library.entities.localSong import LocalSong
from app.domain.metadata.services import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
)
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

    def execute(
        self,
        on_progress: Callable[[ScanLocalFolderProgressDto], None] | None = None,
    ) -> ScanLocalFolderResultDto:
        activeLocalFolder = self._local_folder_repository.get_active()
        if activeLocalFolder is None or activeLocalFolder.id is None:
            raise ValueError("No hay una biblioteca local activa para escanear.")

        try:
            discoveredFilePaths = self._local_music_scanner.scanMp3Files(activeLocalFolder.path)
        except FileNotFoundError as error:
            raise ValueError(
                f'La carpeta local "{activeLocalFolder.display_name}" no existe o ya no esta disponible: '
                f"{activeLocalFolder.path}."
            ) from error
        except NotADirectoryError as error:
            raise ValueError(
                f'La ruta guardada para la biblioteca "{activeLocalFolder.display_name}" ya no es una carpeta valida: '
                f"{activeLocalFolder.path}."
            ) from error
        except PermissionError as error:
            raise ValueError(
                f'No se puede leer la carpeta local "{activeLocalFolder.display_name}": '
                f"{activeLocalFolder.path}. Revisa los permisos e intentalo de nuevo."
            ) from error
        totalSongCount = len(discoveredFilePaths)
        discoveredFilePathSet = set(discoveredFilePaths)
        persistedSongs = self._local_song_repository.list_by_folder(activeLocalFolder.id)
        persistedSongsByPath = {song.file_path: song for song in persistedSongs}
        missingCandidateSongsById = {
            song.id: song
            for song in persistedSongs
            if song.id is not None and song.file_path not in discoveredFilePathSet
        }
        createdSongCount = 0
        updatedSongCount = 0
        existingSongCount = 0
        missingSongCount = 0
        movedSongCount = 0
        processedSongCount = 0

        self._emitProgress(on_progress, processedSongCount, totalSongCount)

        for filePath in discoveredFilePaths:
            existingSong = persistedSongsByPath.get(filePath)
            metadata = self._local_song_metadata_reader.readMetadata(filePath)
            if existingSong is not None:
                updatedSong = self._buildLocalSong(
                    filePath=filePath,
                    metadata=metadata,
                    active_local_folder_id=activeLocalFolder.id,
                    existing_song=existingSong,
                )
                self._local_song_repository.save(updatedSong)
                if self._hasSongChanged(existingSong, updatedSong):
                    updatedSongCount += 1
                else:
                    existingSongCount += 1
                processedSongCount += 1
                self._emitProgress(on_progress, processedSongCount, totalSongCount)
                continue

            movedSong = self._findMovedSongCandidate(
                filePath=filePath,
                metadata=metadata,
                missing_candidate_songs=missingCandidateSongsById.values(),
            )
            if movedSong is not None:
                updatedSong = self._buildLocalSong(
                    filePath=filePath,
                    metadata=metadata,
                    active_local_folder_id=activeLocalFolder.id,
                    existing_song=movedSong,
                )
                self._local_song_repository.save(updatedSong)
                if movedSong.id is not None:
                    missingCandidateSongsById.pop(movedSong.id, None)
                updatedSongCount += 1
                movedSongCount += 1
                processedSongCount += 1
                self._emitProgress(on_progress, processedSongCount, totalSongCount)
                continue

            self._local_song_repository.save(
                self._buildLocalSong(
                    filePath=filePath,
                    metadata=metadata,
                    active_local_folder_id=activeLocalFolder.id,
                )
            )
            createdSongCount += 1
            processedSongCount += 1
            self._emitProgress(on_progress, processedSongCount, totalSongCount)

        for missingSong in missingCandidateSongsById.values():
            if not missingSong.is_available:
                continue

            self._local_song_repository.save(
                LocalSong(
                    id=missingSong.id,
                    local_folder_id=missingSong.local_folder_id,
                    download_id=missingSong.download_id,
                    file_path=missingSong.file_path,
                    file_name=missingSong.file_name,
                    is_available=False,
                    title=missingSong.title,
                    artist=missingSong.artist,
                    normalized_title=missingSong.normalized_title,
                    normalized_artist=missingSong.normalized_artist,
                    album=missingSong.album,
                    release_year=missingSong.release_year,
                    track_number_album=missingSong.track_number_album,
                    duration_seconds=missingSong.duration_seconds,
                )
            )
            missingSongCount += 1

        return ScanLocalFolderResultDto(
            local_folder_id=activeLocalFolder.id,
            local_folder_name=activeLocalFolder.display_name,
            scanned_file_count=totalSongCount,
            created_song_count=createdSongCount,
            updated_song_count=updatedSongCount,
            existing_song_count=existingSongCount,
            missing_song_count=missingSongCount,
            moved_song_count=movedSongCount,
        )

    def _emitProgress(
        self,
        on_progress: Callable[[ScanLocalFolderProgressDto], None] | None,
        processed_song_count: int,
        total_song_count: int,
    ) -> None:
        if on_progress is None:
            return

        on_progress(
            ScanLocalFolderProgressDto(
                processed_song_count=processed_song_count,
                total_song_count=total_song_count,
            )
        )

    def _buildLocalSong(
        self,
        filePath: str,
        metadata: LocalSongMetadataDto,
        active_local_folder_id: int,
        existing_song: LocalSong | None = None,
    ) -> LocalSong:
        normalized_title = normalizeMusicComparisonTitle(metadata.title)
        normalized_artist = normalizeMusicComparisonArtist(metadata.artist)
        return LocalSong(
            id=existing_song.id if existing_song is not None else None,
            local_folder_id=active_local_folder_id,
            download_id=existing_song.download_id if existing_song is not None else None,
            file_path=filePath,
            file_name=PureWindowsPath(filePath).name,
            is_available=True,
            title=metadata.title,
            artist=metadata.artist,
            normalized_title=normalized_title,
            normalized_artist=normalized_artist,
            album=metadata.album,
            release_year=metadata.release_year,
            track_number_album=metadata.track_number_album,
            duration_seconds=metadata.duration_seconds,
        )

    def _findMovedSongCandidate(
        self,
        filePath: str,
        metadata: LocalSongMetadataDto,
        missing_candidate_songs: Iterable[LocalSong],
    ) -> LocalSong | None:
        targetSignature = self._buildMoveSignature(PureWindowsPath(filePath).name, metadata)
        matchingSongs = [
            song
            for song in missing_candidate_songs
            if self._buildMoveSignature(
                song.file_name,
                LocalSongMetadataDto(
                    title=song.title,
                    artist=song.artist,
                    album=song.album,
                    release_year=song.release_year,
                    track_number_album=song.track_number_album,
                    duration_seconds=song.duration_seconds,
                ),
            )
            == targetSignature
        ]
        if len(matchingSongs) != 1:
            return None
        return matchingSongs[0]

    def _buildMoveSignature(self, fileName: str, metadata: LocalSongMetadataDto) -> tuple:
        return (
            fileName.strip().lower(),
            metadata.title.strip().lower(),
            metadata.artist.strip().lower(),
            metadata.album.strip().lower(),
            metadata.release_year,
            metadata.track_number_album,
            round(metadata.duration_seconds, 1),
        )

    def _hasSongChanged(self, persisted_song: LocalSong, scanned_song: LocalSong) -> bool:
        return (
            persisted_song.file_path != scanned_song.file_path
            or persisted_song.file_name != scanned_song.file_name
            or persisted_song.is_available != scanned_song.is_available
            or persisted_song.title != scanned_song.title
            or persisted_song.artist != scanned_song.artist
            or persisted_song.normalized_title != scanned_song.normalized_title
            or persisted_song.normalized_artist != scanned_song.normalized_artist
            or persisted_song.album != scanned_song.album
            or persisted_song.release_year != scanned_song.release_year
            or persisted_song.track_number_album != scanned_song.track_number_album
            or round(persisted_song.duration_seconds, 1) != round(scanned_song.duration_seconds, 1)
        )
