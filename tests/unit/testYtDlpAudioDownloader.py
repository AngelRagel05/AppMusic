from __future__ import annotations

from pathlib import Path

import app.infrastructure.downloads.youtube.ytDlpAudioDownloader as downloader_module
import pytest
from app.infrastructure.downloads.youtube import YtDlpAudioDownloader
from app.shared.exceptions import OperationCancelledError
from yt_dlp.utils import DownloadError


class SuccessfulYoutubeDL:
    options: dict = {}

    def __init__(self, options: dict) -> None:
        type(self).options = options

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def extract_info(self, _source_url: str, *, download: bool) -> dict:
        assert download is True
        progress_hook = self.options["progress_hooks"][0]
        progress_hook(
            {
                "status": "downloading",
                "downloaded_bytes": 50,
                "total_bytes": 100,
            }
        )
        progress_hook({"status": "finished"})
        return {
            "id": "video",
            "ext": "webm",
            "title": "Song",
            "artist": "Artist",
        }

    def prepare_filename(self, _info: dict) -> str:
        original_path = Path(self.options["outtmpl"].replace(
            "%(title).180B",
            "Song",
        ).replace("%(id)s", "video").replace("%(ext)s", "webm"))
        original_path.with_suffix(".mp3").write_bytes(b"mp3")
        return str(original_path)


class FailingYoutubeDL(SuccessfulYoutubeDL):
    def extract_info(self, _source_url: str, *, download: bool) -> dict:
        assert download is True
        raise DownloadError("network failure")


def test_downloader_configures_conversion_metadata_progress_and_temporary_path(
    tmp_path,
    monkeypatch,
) -> None:
    ffmpeg_path = tmp_path / "ffmpeg.exe"
    ffmpeg_path.write_bytes(b"binary")
    destination = tmp_path / "library"
    destination.mkdir()
    temporary_folder = tmp_path / "temporary"
    monkeypatch.setattr(downloader_module, "YoutubeDL", SuccessfulYoutubeDL)
    progress: list[tuple[float, str | None]] = []

    result = YtDlpAudioDownloader(
        str(ffmpeg_path),
        socket_timeout_seconds=15,
        temporary_folder=str(temporary_folder),
    ).download(
        source_url="https://youtu.be/video",
        destination_folder=str(destination),
        on_progress=lambda value, message: progress.append((value, message)),
        is_cancelled=lambda: False,
    )

    assert Path(result.file_path).is_file()
    assert result.title == "Song"
    assert progress[0][0] == 47.5
    assert progress[-1][0] == 100
    assert SuccessfulYoutubeDL.options["socket_timeout"] == 15
    assert SuccessfulYoutubeDL.options["paths"]["temp"] == str(
        temporary_folder.resolve()
    )
    assert {
        postprocessor["key"]
        for postprocessor in SuccessfulYoutubeDL.options["postprocessors"]
    } == {"FFmpegExtractAudio", "FFmpegMetadata"}


def test_downloader_maps_yt_dlp_failures_to_an_application_error(
    tmp_path,
    monkeypatch,
) -> None:
    ffmpeg_path = tmp_path / "ffmpeg.exe"
    ffmpeg_path.write_bytes(b"binary")
    monkeypatch.setattr(downloader_module, "YoutubeDL", FailingYoutubeDL)

    with pytest.raises(ValueError, match="yt-dlp no pudo descargar"):
        YtDlpAudioDownloader(str(ffmpeg_path)).download(
            source_url="https://youtu.be/video",
            destination_folder=str(tmp_path),
            on_progress=lambda _value, _message: None,
            is_cancelled=lambda: False,
        )


def test_downloader_stops_from_the_native_progress_hook(
    tmp_path,
    monkeypatch,
) -> None:
    ffmpeg_path = tmp_path / "ffmpeg.exe"
    ffmpeg_path.write_bytes(b"binary")
    monkeypatch.setattr(downloader_module, "YoutubeDL", SuccessfulYoutubeDL)

    with pytest.raises(OperationCancelledError):
        YtDlpAudioDownloader(str(ffmpeg_path)).download(
            source_url="https://youtu.be/video",
            destination_folder=str(tmp_path),
            on_progress=lambda _value, _message: None,
            is_cancelled=lambda: True,
        )
