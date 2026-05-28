from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from music_app.app.domain.entities.song import Song
from music_app.app.domain.services.song_repository import SongRepository
from music_app.app.infrastructure.database.models import SongModel


class SqlAlchemySongRepository(SongRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_path(self, path: str) -> Song | None:
        statement = select(SongModel).where(SongModel.path == path)
        model = self._session.execute(statement).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def add(self, song: Song) -> Song:
        model = SongModel(
            path=song.path,
            title=song.title,
            artist=song.artist,
            album=song.album,
            year=song.year,
            track_number=song.track_number,
            duration=song.duration,
            created_at=song.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: SongModel) -> Song:
        return Song(
            id=model.id,
            path=model.path,
            title=model.title,
            artist=model.artist,
            album=model.album,
            year=model.year,
            track_number=model.track_number,
            duration=model.duration,
            created_at=model.created_at,
        )

