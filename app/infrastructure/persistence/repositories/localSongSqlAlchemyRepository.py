from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.infrastructure.persistence.database.models import LocalSong as LocalSongModel


class LocalSongSqlAlchemyRepository(LocalSongRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, local_song_id: int) -> LocalSong | None:
        model = self._session.get(LocalSongModel, local_song_id)
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_folder(self, local_folder_id: int) -> Sequence[LocalSong]:
        statement: Select[tuple[LocalSongModel]] = (
            select(LocalSongModel)
            .where(LocalSongModel.local_folder_id == local_folder_id)
            .order_by(
                LocalSongModel.file_name.asc(),
                LocalSongModel.file_path.asc(),
            )
        )
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def get_by_file_path(self, file_path: str) -> LocalSong | None:
        statement: Select[tuple[LocalSongModel]] = select(LocalSongModel).where(
            LocalSongModel.file_path == file_path
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, local_song: LocalSong) -> LocalSong:
        model = None
        if local_song.id is not None:
            model = self._session.get(LocalSongModel, local_song.id)

        if model is None:
            statement: Select[tuple[LocalSongModel]] = select(LocalSongModel).where(
                LocalSongModel.file_path == local_song.file_path
            )
            model = self._session.scalar(statement)

        if model is None:
            model = LocalSongModel(
                local_folder_id=local_song.local_folder_id or 0,
                download_id=local_song.download_id,
                file_path=local_song.file_path,
                file_name=local_song.file_name,
                is_available=local_song.is_available,
                title=local_song.title,
                artist=local_song.artist,
                normalized_title=local_song.normalized_title,
                normalized_artist=local_song.normalized_artist,
                album=local_song.album,
                release_year=local_song.release_year,
                track_number_album=local_song.track_number_album,
                duration_seconds=local_song.duration_seconds,
            )
            self._session.add(model)
        else:
            model.local_folder_id = local_song.local_folder_id or model.local_folder_id
            model.download_id = local_song.download_id
            model.file_path = local_song.file_path
            model.file_name = local_song.file_name
            model.is_available = local_song.is_available
            model.title = local_song.title
            model.artist = local_song.artist
            model.normalized_title = local_song.normalized_title
            model.normalized_artist = local_song.normalized_artist
            model.album = local_song.album
            model.release_year = local_song.release_year
            model.track_number_album = local_song.track_number_album
            model.duration_seconds = local_song.duration_seconds

        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: LocalSongModel) -> LocalSong:
        return LocalSong(
            id=model.id,
            local_folder_id=model.local_folder_id,
            download_id=model.download_id,
            file_path=model.file_path,
            file_name=model.file_name,
            is_available=model.is_available,
            title=model.title,
            artist=model.artist,
            normalized_title=model.normalized_title,
            normalized_artist=model.normalized_artist,
            album=model.album,
            release_year=model.release_year,
            track_number_album=model.track_number_album,
            duration_seconds=model.duration_seconds,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
