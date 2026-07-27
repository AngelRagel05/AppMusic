from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from app.application.dto.downloadedAudioDto import DownloadedAudioDto
from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.domain.downloads.repositories import DownloadRepository
from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.metadata.services import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
)
from app.shared.exceptions import OperationCancelledError


class AudioDownloaderPort(Protocol):
    def download(
        self,
        *,
        source_url: str,
        destination_folder: str,
        on_progress: Callable[[float, str | None], None],
        is_cancelled: Callable[[], bool],
    ) -> DownloadedAudioDto:
        ...


class LocalSongMetadataReaderPort(Protocol):
    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        ...


class DownloadAudioUseCase:
    def __init__(
        self,
        download_repository: DownloadRepository,
        local_folder_repository: LocalFolderRepository,
        local_song_repository: LocalSongRepository,
        audio_downloader: AudioDownloaderPort,
        metadata_reader: LocalSongMetadataReaderPort,
        commit: Callable[[], None],
        rollback: Callable[[], None],
    ) -> None:
        self._download_repository = download_repository
        self._local_folder_repository = local_folder_repository
        self._local_song_repository = local_song_repository
        self._audio_downloader = audio_downloader
        self._metadata_reader = metadata_reader
        self._commit = commit
        self._rollback = rollback

    def execute(
        self,
        *,
        task_id: str,
        local_folder_id: int,
        source_url: str,
        youtube_playlist_item_id: int | None,
        source_title: str | None,
        source_artist: str | None,
        on_progress: Callable[[float, str | None], None],
        is_cancelled: Callable[[], bool],
    ) -> dict:
        local_folder = next(
            (
                folder
                for folder in self._local_folder_repository.list_all()
                if folder.id == local_folder_id
            ),
            None,
        )
        if local_folder is None:
            raise ValueError("La biblioteca de destino no existe.")
        destination_folder = Path(local_folder.path).resolve(strict=False)
        if not destination_folder.is_dir():
            raise ValueError("La biblioteca de destino no esta disponible.")
        if not source_url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            raise ValueError("La URL de descarga debe pertenecer a YouTube.")
        completed_download = self._download_repository.findCompleted(
            local_folder_id=local_folder_id,
            source_url=source_url,
            youtube_playlist_item_id=youtube_playlist_item_id,
        )
        if (
            completed_download is not None
            and completed_download.target_file_path
            and Path(completed_download.target_file_path).is_file()
        ):
            raise ValueError(
                "Este origen ya tiene una descarga completada en la biblioteca."
            )

        download = self._download_repository.createPending(
            task_id=task_id,
            local_folder_id=local_folder_id,
            source_url=source_url,
            youtube_playlist_item_id=youtube_playlist_item_id,
            source_title=source_title,
            source_artist=source_artist,
        )
        if download.id is None:
            raise RuntimeError("No se pudo persistir el intento de descarga.")

        download_id = download.id
        self._download_repository.markInProgress(download_id)

        def reportProgress(progress: float, message: str | None) -> None:
            if is_cancelled():
                raise OperationCancelledError("La descarga fue cancelada por el usuario.")
            self._download_repository.updateProgress(download_id, progress)
            on_progress(progress, message)

        try:
            downloaded_audio = self._audio_downloader.download(
                source_url=source_url,
                destination_folder=str(destination_folder),
                on_progress=reportProgress,
                is_cancelled=is_cancelled,
            )
            if is_cancelled():
                raise OperationCancelledError(
                    "La descarga fue cancelada por el usuario."
                )
            file_path = Path(downloaded_audio.file_path).resolve(strict=True)
            if not file_path.is_relative_to(destination_folder):
                raise ValueError("La descarga termino fuera de la biblioteca autorizada.")

            metadata = self._metadata_reader.readMetadata(str(file_path))
            local_song = self._local_song_repository.save(
                LocalSong(
                    local_folder_id=local_folder_id,
                    download_id=download_id,
                    file_path=str(file_path),
                    file_name=file_path.name,
                    is_available=True,
                    title=metadata.title,
                    artist=metadata.artist,
                    normalized_title=normalizeMusicComparisonTitle(metadata.title),
                    normalized_artist=normalizeMusicComparisonArtist(metadata.artist),
                    album=metadata.album,
                    release_year=metadata.release_year,
                    track_number_album=metadata.track_number_album,
                    duration_seconds=metadata.duration_seconds,
                )
            )
            completed = self._download_repository.markCompleted(
                download_id,
                target_file_path=str(file_path),
                source_title=downloaded_audio.title or source_title,
                source_artist=downloaded_audio.artist or source_artist,
            )
            self._commit()
            return {
                "download_id": completed.id,
                "local_song_id": local_song.id,
                "target_file_path": completed.target_file_path,
            }
        except OperationCancelledError as error:
            self._rollback()
            self._download_repository.markFailed(
                download_id,
                error_message=str(error),
                cancelled=True,
            )
            raise
        except Exception as error:
            self._rollback()
            self._download_repository.markFailed(
                download_id,
                error_message=str(error) or error.__class__.__name__,
                cancelled=False,
            )
            raise
