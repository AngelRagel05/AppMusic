from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.playlists.entities.youtubePlaylist import YoutubePlaylist
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.infrastructure.database.models import YoutubePlaylist as YoutubePlaylistModel


class YoutubePlaylistSqlAlchemyRepository(YoutubePlaylistRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[YoutubePlaylist]:
        statement: Select[tuple[YoutubePlaylistModel]] = select(YoutubePlaylistModel).order_by(
            YoutubePlaylistModel.title.asc(),
            YoutubePlaylistModel.playlist_url.asc(),
        )
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def get_active(self) -> YoutubePlaylist | None:
        statement: Select[tuple[YoutubePlaylistModel]] = select(YoutubePlaylistModel).where(
            YoutubePlaylistModel.is_active.is_(True)
        )
        model = self._session.scalar(statement)
        if model is None:
            return None

        return self._to_entity(model)

    def save_as_active(
        self,
        playlist_url: str,
        external_playlist_id: str,
        title: str,
    ) -> YoutubePlaylist:
        self._session.query(YoutubePlaylistModel).update(
            {YoutubePlaylistModel.is_active: False}
        )

        statement: Select[tuple[YoutubePlaylistModel]] = select(YoutubePlaylistModel).where(
            YoutubePlaylistModel.external_playlist_id == external_playlist_id
        )
        model = self._session.scalar(statement)

        if model is None:
            model = YoutubePlaylistModel(
                playlist_url=playlist_url,
                external_playlist_id=external_playlist_id,
                title=title,
                is_active=True,
            )
            self._session.add(model)
        else:
            model.playlist_url = playlist_url
            model.title = title
            model.is_active = True

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def activate(self, youtube_playlist_id: int) -> YoutubePlaylist:
        statement: Select[tuple[YoutubePlaylistModel]] = select(YoutubePlaylistModel).where(
            YoutubePlaylistModel.id == youtube_playlist_id
        )
        model = self._session.scalar(statement)
        if model is None:
            msg = "La playlist seleccionada no existe."
            raise ValueError(msg)

        self._session.query(YoutubePlaylistModel).update(
            {YoutubePlaylistModel.is_active: False}
        )
        model.is_active = True
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def update(
        self,
        youtube_playlist_id: int,
        playlist_url: str,
        external_playlist_id: str,
        title: str,
    ) -> YoutubePlaylist:
        statement: Select[tuple[YoutubePlaylistModel]] = select(YoutubePlaylistModel).where(
            YoutubePlaylistModel.id == youtube_playlist_id
        )
        model = self._session.scalar(statement)
        if model is None:
            msg = "La playlist seleccionada no existe."
            raise ValueError(msg)

        duplicate_id_statement: Select[tuple[YoutubePlaylistModel]] = select(
            YoutubePlaylistModel
        ).where(
            YoutubePlaylistModel.external_playlist_id == external_playlist_id,
            YoutubePlaylistModel.id != youtube_playlist_id,
        )
        duplicate_id_model = self._session.scalar(duplicate_id_statement)
        if duplicate_id_model is not None:
            msg = "Ya existe una playlist guardada con ese identificador de YouTube."
            raise ValueError(msg)

        duplicate_url_statement: Select[tuple[YoutubePlaylistModel]] = select(
            YoutubePlaylistModel
        ).where(
            YoutubePlaylistModel.playlist_url == playlist_url,
            YoutubePlaylistModel.id != youtube_playlist_id,
        )
        duplicate_url_model = self._session.scalar(duplicate_url_statement)
        if duplicate_url_model is not None:
            msg = "Ya existe una playlist guardada con esa URL."
            raise ValueError(msg)

        model.playlist_url = playlist_url
        model.external_playlist_id = external_playlist_id
        model.title = title
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, youtube_playlist_id: int) -> None:
        statement: Select[tuple[YoutubePlaylistModel]] = select(YoutubePlaylistModel).where(
            YoutubePlaylistModel.id == youtube_playlist_id
        )
        model = self._session.scalar(statement)
        if model is None:
            msg = "La playlist seleccionada no existe."
            raise ValueError(msg)

        self._session.delete(model)
        self._session.commit()

    def _to_entity(self, model: YoutubePlaylistModel) -> YoutubePlaylist:
        return YoutubePlaylist(
            id=model.id,
            playlist_url=model.playlist_url,
            external_playlist_id=model.external_playlist_id,
            title=model.title,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
