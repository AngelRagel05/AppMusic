from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.dto.localSongMetadataUpdateDto import LocalSongMetadataUpdateDto
from app.application.use_cases.metadata.localSongMapping import mapLocalSongToDto
from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.metadata.services import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
)


class LocalSongMetadataWriterPort(Protocol):
    def writeMetadata(
        self,
        filePath: str,
        metadata: LocalSongMetadataUpdateDto,
    ) -> None:
        ...


class LocalSongMetadataReaderPort(Protocol):
    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        ...


class UpdateLocalSongMetadataUseCase:
    def __init__(
        self,
        local_song_repository: LocalSongRepository,
        local_folder_repository: LocalFolderRepository,
        metadata_writer: LocalSongMetadataWriterPort,
        metadata_reader: LocalSongMetadataReaderPort,
    ) -> None:
        self._local_song_repository = local_song_repository
        self._local_folder_repository = local_folder_repository
        self._metadata_writer = metadata_writer
        self._metadata_reader = metadata_reader

    def execute(
        self,
        local_song_id: int,
        metadata: LocalSongMetadataUpdateDto,
    ) -> LocalSongDto:
        local_song = self._getValidatedLocalSong(local_song_id)
        normalized_metadata = self._validateMetadata(metadata)
        self._metadata_writer.writeMetadata(local_song.file_path, normalized_metadata)
        persisted_metadata = self._metadata_reader.readMetadata(local_song.file_path)
        updated_song = self._local_song_repository.save(
            self._mergeMetadata(local_song, persisted_metadata)
        )
        return mapLocalSongToDto(updated_song)

    def _getValidatedLocalSong(self, local_song_id: int) -> LocalSong:
        if local_song_id <= 0:
            raise ValueError("El id de la cancion local no es valido.")
        local_song = self._local_song_repository.get_by_id(local_song_id)
        if local_song is None:
            raise ValueError("La cancion local seleccionada no existe.")
        local_folder = next(
            (
                folder
                for folder in self._local_folder_repository.list_all()
                if folder.id == local_song.local_folder_id
            ),
            None,
        )
        if local_folder is None:
            raise ValueError("La biblioteca de la cancion ya no existe.")

        song_path = Path(local_song.file_path).resolve(strict=False)
        folder_path = Path(local_folder.path).resolve(strict=False)
        if not song_path.is_relative_to(folder_path):
            raise ValueError("La cancion queda fuera de la biblioteca registrada.")
        if song_path.suffix.casefold() != ".mp3" or not song_path.is_file():
            raise ValueError("El archivo MP3 ya no esta disponible.")
        return local_song

    def _validateMetadata(
        self,
        metadata: LocalSongMetadataUpdateDto,
    ) -> LocalSongMetadataUpdateDto:
        title = metadata.title.strip()
        artist = metadata.artist.strip()
        album = metadata.album.strip()
        if not title:
            raise ValueError("El titulo es obligatorio.")
        if metadata.release_year < 0 or metadata.release_year > 9999:
            raise ValueError("El año de publicacion no es valido.")
        if metadata.track_number_album < 0:
            raise ValueError("El numero de pista no puede ser negativo.")
        return LocalSongMetadataUpdateDto(
            title=title,
            artist=artist,
            album=album,
            release_year=metadata.release_year,
            track_number_album=metadata.track_number_album,
        )

    def _mergeMetadata(
        self,
        local_song: LocalSong,
        metadata: LocalSongMetadataDto,
    ) -> LocalSong:
        return LocalSong(
            id=local_song.id,
            local_folder_id=local_song.local_folder_id,
            download_id=local_song.download_id,
            file_path=local_song.file_path,
            file_name=local_song.file_name,
            is_available=True,
            title=metadata.title,
            artist=metadata.artist,
            normalized_title=normalizeMusicComparisonTitle(metadata.title),
            normalized_artist=normalizeMusicComparisonArtist(metadata.artist),
            album=metadata.album,
            release_year=metadata.release_year,
            track_number_album=metadata.track_number_album,
            duration_seconds=metadata.duration_seconds,
            created_at=local_song.created_at,
            updated_at=local_song.updated_at,
        )
