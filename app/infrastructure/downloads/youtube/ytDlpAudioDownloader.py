from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.application.dto.downloadedAudioDto import DownloadedAudioDto
from app.shared.exceptions import OperationCancelledError


class YtDlpAudioDownloader:
    def __init__(
        self,
        ffmpeg_path: str = "ffmpeg",
        *,
        socket_timeout_seconds: float = 30.0,
        temporary_folder: str | None = None,
    ) -> None:
        self._ffmpeg_path = ffmpeg_path
        self._socket_timeout_seconds = socket_timeout_seconds
        self._temporary_folder = temporary_folder

    def isAvailable(self) -> bool:
        return self._resolveFfmpegPath() is not None

    def download(
        self,
        *,
        source_url: str,
        destination_folder: str,
        on_progress: Callable[[float, str | None], None],
        is_cancelled: Callable[[], bool],
    ) -> DownloadedAudioDto:
        ffmpeg_path = self._resolveFfmpegPath()
        if ffmpeg_path is None:
            raise ValueError(
                "FFmpeg no esta disponible. Configura FFMPEG_PATH antes de descargar."
            )

        destination = Path(destination_folder).resolve(strict=True)
        output_template = str(destination / "%(title).180B [%(id)s].%(ext)s")
        temporary_folder = (
            Path(self._temporary_folder).resolve(strict=False)
            if self._temporary_folder
            else None
        )
        if temporary_folder is not None:
            temporary_folder.mkdir(parents=True, exist_ok=True)

        def progressHook(payload: dict) -> None:
            if is_cancelled():
                raise OperationCancelledError(
                    "La descarga fue cancelada por el usuario."
                )
            status = payload.get("status")
            if status == "downloading":
                downloaded_bytes = float(payload.get("downloaded_bytes") or 0)
                total_bytes = float(
                    payload.get("total_bytes")
                    or payload.get("total_bytes_estimate")
                    or 0
                )
                progress = (
                    min(95.0, downloaded_bytes * 95.0 / total_bytes)
                    if total_bytes > 0
                    else 0.0
                )
                on_progress(progress, "Descargando audio…")
            elif status == "finished":
                on_progress(96.0, "Convirtiendo a MP3…")

        options = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "windowsfilenames": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": self._socket_timeout_seconds,
            "ffmpeg_location": ffmpeg_path,
            "progress_hooks": [progressHook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
            ],
        }
        if temporary_folder is not None:
            options["paths"] = {"temp": str(temporary_folder)}
        try:
            with YoutubeDL(options) as youtube_dl:
                info = youtube_dl.extract_info(source_url, download=True)
                if info is None:
                    raise ValueError("YouTube no devolvio informacion descargable.")
                original_path = Path(youtube_dl.prepare_filename(info))
        except OperationCancelledError:
            raise
        except DownloadError as error:
            if is_cancelled():
                raise OperationCancelledError(
                    "La descarga fue cancelada por el usuario."
                ) from error
            raise ValueError(f"yt-dlp no pudo descargar el audio: {error}") from error

        mp3_path = original_path.with_suffix(".mp3").resolve(strict=False)
        if not mp3_path.is_file():
            raise ValueError("FFmpeg no genero el archivo MP3 esperado.")
        on_progress(100.0, "MP3 creado e indexado.")
        return DownloadedAudioDto(
            file_path=str(mp3_path),
            title=str(info.get("title") or mp3_path.stem),
            artist=str(
                info.get("artist")
                or info.get("uploader")
                or info.get("channel")
                or ""
            ),
        )

    def _resolveFfmpegPath(self) -> str | None:
        configured_path = Path(self._ffmpeg_path)
        if configured_path.is_file():
            return str(configured_path.resolve())
        return shutil.which(self._ffmpeg_path)
