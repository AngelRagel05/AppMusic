from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Select, delete, func, select
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

    def count_by_playlist(self, youtube_playlist_id: int) -> int:
        statement = select(func.count(YoutubePlaylistItemModel.id)).where(
            YoutubePlaylistItemModel.youtube_playlist_id == youtube_playlist_id
        )
        return int(self._session.scalar(statement) or 0)

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
        existing_models = self._session.scalars(
            select(YoutubePlaylistItemModel).where(
                YoutubePlaylistItemModel.youtube_playlist_id == youtube_playlist_id
            )
        ).all()
        existing_models_by_external_video_id = {
            model.external_video_id: model for model in existing_models
        }
        incoming_external_video_ids = {item.external_video_id for item in items}

        for existing_model in existing_models:
            if existing_model.external_video_id in incoming_external_video_ids:
                continue
            self._session.delete(existing_model)

        for item in items:
            existing_model = existing_models_by_external_video_id.get(item.external_video_id)
            if existing_model is None:
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
                continue

            if not self._hasItemChanged(existing_model, item):
                continue

            existing_model.position = item.position
            existing_model.raw_title = item.raw_title
            existing_model.raw_channel_name = item.raw_channel_name
            existing_model.normalized_title = item.normalized_title
            existing_model.normalized_artist = item.normalized_artist
            existing_model.duration_seconds = item.duration_seconds
            existing_model.published_at = item.published_at

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

    def _hasItemChanged(
        self,
        existing_model: YoutubePlaylistItemModel,
        incoming_item: YoutubePlaylistItem,
    ) -> bool:
        return (
            existing_model.position != incoming_item.position
            or existing_model.raw_title != incoming_item.raw_title
            or existing_model.raw_channel_name != incoming_item.raw_channel_name
            or existing_model.normalized_title != incoming_item.normalized_title
            or existing_model.normalized_artist != incoming_item.normalized_artist
            or existing_model.duration_seconds != incoming_item.duration_seconds
            or self._normalizePublishedAt(existing_model.published_at)
            != self._normalizePublishedAt(incoming_item.published_at)
        )
