from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.downloads.entities import Download


class DownloadRepository(ABC):
    @abstractmethod
    def createPending(
        self,
        *,
        task_id: str,
        local_folder_id: int,
        source_url: str,
        youtube_playlist_item_id: int | None,
        source_title: str | None,
        source_artist: str | None,
    ) -> Download:
        raise NotImplementedError

    @abstractmethod
    def getById(self, download_id: int) -> Download | None:
        raise NotImplementedError

    @abstractmethod
    def listRecent(self, *, limit: int = 100) -> list[Download]:
        raise NotImplementedError

    @abstractmethod
    def findCompleted(
        self,
        *,
        local_folder_id: int,
        source_url: str,
        youtube_playlist_item_id: int | None,
    ) -> Download | None:
        raise NotImplementedError

    @abstractmethod
    def markInProgress(self, download_id: int) -> Download:
        raise NotImplementedError

    @abstractmethod
    def updateProgress(self, download_id: int, progress_percent: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def markCompleted(
        self,
        download_id: int,
        *,
        target_file_path: str,
        source_title: str | None,
        source_artist: str | None,
    ) -> Download:
        raise NotImplementedError

    @abstractmethod
    def markFailed(
        self,
        download_id: int,
        *,
        error_message: str,
        cancelled: bool,
    ) -> Download:
        raise NotImplementedError
