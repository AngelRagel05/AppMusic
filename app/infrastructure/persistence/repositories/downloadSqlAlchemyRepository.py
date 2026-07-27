from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Select, desc, select
from sqlalchemy.orm import Session

from app.domain.downloads.entities import Download
from app.domain.downloads.repositories import DownloadRepository
from app.infrastructure.persistence.database.models import Download as DownloadModel


class DownloadSqlAlchemyRepository(DownloadRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

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
        model = DownloadModel(
            task_id=task_id,
            local_folder_id=local_folder_id,
            youtube_playlist_item_id=youtube_playlist_item_id,
            source_url=source_url,
            source_title=source_title,
            source_artist=source_artist,
            status="pending",
            progress_percent=0.0,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._toEntity(model)

    def getById(self, download_id: int) -> Download | None:
        model = self._session.get(DownloadModel, download_id)
        return self._toEntity(model) if model is not None else None

    def listRecent(self, *, limit: int = 100) -> list[Download]:
        statement: Select[tuple[DownloadModel]] = (
            select(DownloadModel)
            .order_by(desc(DownloadModel.created_at), desc(DownloadModel.id))
            .limit(limit)
        )
        return [
            self._toEntity(model)
            for model in self._session.scalars(statement).all()
        ]

    def findCompleted(
        self,
        *,
        local_folder_id: int,
        source_url: str,
        youtube_playlist_item_id: int | None,
    ) -> Download | None:
        source_condition = (
            DownloadModel.youtube_playlist_item_id == youtube_playlist_item_id
            if youtube_playlist_item_id is not None
            else DownloadModel.source_url == source_url
        )
        statement = (
            select(DownloadModel)
            .where(
                DownloadModel.local_folder_id == local_folder_id,
                DownloadModel.status == "completed",
                source_condition,
            )
            .order_by(desc(DownloadModel.finished_at), desc(DownloadModel.id))
            .limit(1)
        )
        model = self._session.scalar(statement)
        return self._toEntity(model) if model is not None else None

    def markInProgress(self, download_id: int) -> Download:
        model = self._getRequired(download_id)
        model.status = "in_progress"
        model.started_at = datetime.now(UTC)
        model.error_message = None
        self._session.commit()
        self._session.refresh(model)
        return self._toEntity(model)

    def updateProgress(self, download_id: int, progress_percent: float) -> None:
        model = self._getRequired(download_id)
        model.progress_percent = min(100.0, max(0.0, float(progress_percent)))
        self._session.commit()

    def markCompleted(
        self,
        download_id: int,
        *,
        target_file_path: str,
        source_title: str | None,
        source_artist: str | None,
    ) -> Download:
        model = self._getRequired(download_id)
        model.status = "completed"
        model.progress_percent = 100.0
        model.target_file_path = target_file_path
        model.source_title = source_title
        model.source_artist = source_artist
        model.error_message = None
        model.finished_at = datetime.now(UTC)
        self._session.flush()
        return self._toEntity(model)

    def markFailed(
        self,
        download_id: int,
        *,
        error_message: str,
        cancelled: bool,
    ) -> Download:
        model = self._getRequired(download_id)
        model.status = "cancelled" if cancelled else "failed"
        model.error_message = error_message[:2048]
        model.finished_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(model)
        return self._toEntity(model)

    def _getRequired(self, download_id: int) -> DownloadModel:
        model = self._session.get(DownloadModel, download_id)
        if model is None:
            raise ValueError("La descarga seleccionada no existe.")
        return model

    def _toEntity(self, model: DownloadModel) -> Download:
        return Download(
            id=model.id,
            youtube_playlist_item_id=model.youtube_playlist_item_id,
            local_folder_id=model.local_folder_id,
            task_id=model.task_id,
            source_url=model.source_url,
            source_title=model.source_title,
            source_artist=model.source_artist,
            status=model.status,
            progress_percent=model.progress_percent,
            target_file_path=model.target_file_path,
            error_message=model.error_message,
            started_at=model.started_at,
            finished_at=model.finished_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
