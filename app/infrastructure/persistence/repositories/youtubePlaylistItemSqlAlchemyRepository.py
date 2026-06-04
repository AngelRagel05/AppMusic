from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Select, delete, select
from sqlalchemy.orm import Session

from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.infrastructure.persistence.database.models import (
    YoutubePlaylistItem as YoutubePlaylistItemModel,
)


class YoutubePlaylistItemSqlAlchemyRepository(YoutubePlaylistItemRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_playlist(self, youtube_playlist_id: int) -> list[YoutubePlaylistItem]:
        statement: Select[tuple[YoutubePlaylistItemModel]] = (
            select(YoutubePlaylistItemModel)
            .where(YoutubePlaylistItemModel.youtube_playlist_id == youtube_playlist_id)
            .order_by(
                YoutubePlaylistItemModel.position.asc(),
                YoutubePlaylistItemModel.external_video_id.asc(),
            )
        )
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def replace_for_playlist(
        self,
        youtube_playlist_id: int,
        items: list[YoutubePlaylistItem],
    ) -> list[YoutubePlaylistItem]:
        self._session.execute(
            delete(YoutubePlaylistItemModel).where(
                YoutubePlaylistItemModel.youtube_playlist_id == youtube_playlist_id
            )
        )

        for item in items:
            self._session.add(
                YoutubePlaylistItemModel(
                    youtube_playlist_id=youtube_playlist_id,
                    external_video_id=item.external_video_id,
                    position=item.position,
                    raw_title=item.raw_title,
                    raw_channel_name=item.raw_channel_name,
                    normalized_title=item.normalized_title,
                    normalized_artist=item.normalized_artist,
                    duration_seconds=item.duration_seconds,
                    published_at=item.published_at,
                )
            )

        self._session.commit()
        return self.list_by_playlist(youtube_playlist_id)

    def delete_by_playlist(self, youtube_playlist_id: int) -> None:
        self._session.execute(
            delete(YoutubePlaylistItemModel).where(
                YoutubePlaylistItemModel.youtube_playlist_id == youtube_playlist_id
            )
        )
        self._session.commit()

    def _to_entity(self, model: YoutubePlaylistItemModel) -> YoutubePlaylistItem:
        return YoutubePlaylistItem(
            id=model.id,
            youtube_playlist_id=model.youtube_playlist_id,
            external_video_id=model.external_video_id,
            position=model.position,
            raw_title=model.raw_title,
            raw_channel_name=model.raw_channel_name,
            normalized_title=model.normalized_title,
            normalized_artist=model.normalized_artist,
            duration_seconds=model.duration_seconds,
            published_at=self._normalizePublishedAt(model.published_at),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _normalizePublishedAt(self, published_at: datetime | None) -> datetime | None:
        if published_at is None:
            return None
        if published_at.tzinfo is None:
            return published_at.replace(tzinfo=UTC)
        return published_at.astimezone(UTC)
