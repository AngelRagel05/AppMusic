from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from app.application.dto.downloadedAudioDto import DownloadedAudioDto
from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.use_cases.downloads import DownloadAudioUseCase
from app.domain.downloads.entities import Download
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong
from app.shared.exceptions import OperationCancelledError


class DownloadRepositorySpy:
    def __init__(self, completed: Download | None = None) -> None:
        self.completed = completed
        self.created = False
        self.progress: list[float] = []
        self.failure: tuple[str, bool] | None = None

    def findCompleted(self, **_criteria) -> Download | None:
        return self.completed

    def createPending(self, **values) -> Download:
        self.created = True
        return Download(
            id=11,
            status="pending",
            progress_percent=0,
            **values,
        )

    def markInProgress(self, download_id: int) -> Download:
        assert download_id == 11
        return self._download(status="in_progress")

    def updateProgress(self, download_id: int, progress_percent: float) -> None:
        assert download_id == 11
        self.progress.append(progress_percent)

    def markCompleted(
        self,
        download_id: int,
        *,
        target_file_path: str,
        source_title: str | None,
        source_artist: str | None,
    ) -> Download:
        assert download_id == 11
        return self._download(
            status="completed",
            progress_percent=100,
            target_file_path=target_file_path,
            source_title=source_title,
            source_artist=source_artist,
        )

    def markFailed(
        self,
        download_id: int,
        *,
        error_message: str,
        cancelled: bool,
    ) -> Download:
        assert download_id == 11
        self.failure = (error_message, cancelled)
        return self._download(status="cancelled" if cancelled else "failed")

    @staticmethod
    def _download(**overrides) -> Download:
        values = {
            "id": 11,
            "youtube_playlist_item_id": None,
            "local_folder_id": 3,
            "task_id": "task-1",
            "source_url": "https://youtu.be/video",
            "source_title": None,
            "source_artist": None,
            "status": "pending",
            "progress_percent": 0,
        }
        values.update(overrides)
        return Download(**values)


class LocalFolderRepositoryStub:
    def __init__(self, folder_path: str) -> None:
        self.folder_path = folder_path

    def list_all(self) -> list[LocalFolder]:
        return [
            LocalFolder(
                id=3,
                path=self.folder_path,
                display_name="Biblioteca",
                is_active=True,
            )
        ]


class LocalSongRepositorySpy:
    def __init__(self) -> None:
        self.saved_song: LocalSong | None = None

    def save(self, song: LocalSong) -> LocalSong:
        self.saved_song = replace(song, id=21)
        return self.saved_song


class AudioDownloaderStub:
    def __init__(self, *, cancel_during_progress: bool = False) -> None:
        self.cancel_during_progress = cancel_during_progress
        self.calls = 0

    def download(
        self,
        *,
        source_url: str,
        destination_folder: str,
        on_progress,
        is_cancelled,
    ) -> DownloadedAudioDto:
        self.calls += 1
        assert source_url == "https://youtu.be/video"
        if self.cancel_during_progress:
            on_progress(25, "Descargando")
        target = Path(destination_folder) / "Artist - Song.mp3"
        target.write_bytes(b"fake mp3")
        on_progress(75, "Descargando")
        assert not is_cancelled()
        return DownloadedAudioDto(
            file_path=str(target),
            title="Song",
            artist="Artist",
        )


class MetadataReaderStub:
    def readMetadata(self, _filePath: str) -> LocalSongMetadataDto:
        return LocalSongMetadataDto(
            title="Song",
            artist="Artist",
            album="Album",
            release_year=2026,
            track_number_album=4,
            duration_seconds=200,
        )


def buildUseCase(
    folder_path: str,
    download_repository: DownloadRepositorySpy,
    audio_downloader: AudioDownloaderStub,
):
    song_repository = LocalSongRepositorySpy()
    commits: list[bool] = []
    rollbacks: list[bool] = []
    use_case = DownloadAudioUseCase(
        download_repository,
        LocalFolderRepositoryStub(folder_path),
        song_repository,
        audio_downloader,
        MetadataReaderStub(),
        lambda: commits.append(True),
        lambda: rollbacks.append(True),
    )
    return use_case, song_repository, commits, rollbacks


def test_download_indexes_verified_file_and_commits_once(tmp_path) -> None:
    download_repository = DownloadRepositorySpy()
    downloader = AudioDownloaderStub()
    use_case, song_repository, commits, rollbacks = buildUseCase(
        str(tmp_path),
        download_repository,
        downloader,
    )
    task_progress: list[float] = []

    result = use_case.execute(
        task_id="task-1",
        local_folder_id=3,
        source_url="https://youtu.be/video",
        youtube_playlist_item_id=None,
        source_title=None,
        source_artist=None,
        on_progress=lambda progress, _message: task_progress.append(progress),
        is_cancelled=lambda: False,
    )

    assert result["download_id"] == 11
    assert result["local_song_id"] == 21
    assert download_repository.progress == [75]
    assert task_progress == [75]
    assert song_repository.saved_song is not None
    assert song_repository.saved_song.normalized_title == "song"
    assert song_repository.saved_song.download_id == 11
    assert commits == [True]
    assert rollbacks == []


def test_download_cancellation_is_persisted_only_after_worker_stops(tmp_path) -> None:
    download_repository = DownloadRepositorySpy()
    downloader = AudioDownloaderStub(cancel_during_progress=True)
    use_case, _song_repository, commits, rollbacks = buildUseCase(
        str(tmp_path),
        download_repository,
        downloader,
    )

    with pytest.raises(OperationCancelledError):
        use_case.execute(
            task_id="task-1",
            local_folder_id=3,
            source_url="https://youtu.be/video",
            youtube_playlist_item_id=None,
            source_title=None,
            source_artist=None,
            on_progress=lambda _progress, _message: None,
            is_cancelled=lambda: True,
        )

    assert commits == []
    assert rollbacks == [True]
    assert download_repository.failure is not None
    assert download_repository.failure[1] is True


def test_download_rejects_existing_completed_file(tmp_path) -> None:
    existing_file = tmp_path / "already-downloaded.mp3"
    existing_file.write_bytes(b"existing")
    completed = DownloadRepositorySpy._download(
        status="completed",
        progress_percent=100,
        target_file_path=str(existing_file),
    )
    download_repository = DownloadRepositorySpy(completed=completed)
    downloader = AudioDownloaderStub()
    use_case, _song_repository, commits, rollbacks = buildUseCase(
        str(tmp_path),
        download_repository,
        downloader,
    )

    with pytest.raises(ValueError, match="ya tiene una descarga"):
        use_case.execute(
            task_id="task-1",
            local_folder_id=3,
            source_url="https://youtu.be/video",
            youtube_playlist_item_id=None,
            source_title=None,
            source_artist=None,
            on_progress=lambda _progress, _message: None,
            is_cancelled=lambda: False,
        )

    assert download_repository.created is False
    assert downloader.calls == 0
    assert commits == []
    assert rollbacks == []
