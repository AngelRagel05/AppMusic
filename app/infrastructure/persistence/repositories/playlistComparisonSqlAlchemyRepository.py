from __future__ import annotations

from sqlalchemy import Select, desc, select

from app.domain.playlists.entities.playlistComparison import PlaylistComparison
from app.domain.playlists.repositories.playlistComparisonRepository import (
    PlaylistComparisonRepository,
)
from app.infrastructure.persistence.database.models import (
    PlaylistComparison as PlaylistComparisonModel,
)


class PlaylistComparisonSqlAlchemyRepository(PlaylistComparisonRepository):
    def __init__(self, session) -> None:
        self._session = session

    def create(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> PlaylistComparison:
        model = PlaylistComparisonModel(
            youtube_playlist_id=youtube_playlist_id,
            local_folder_id=local_folder_id,
        )
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)

    def find_latest_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> PlaylistComparison | None:
        statement: Select[tuple[PlaylistComparisonModel]] = (
            select(PlaylistComparisonModel)
            .where(PlaylistComparisonModel.youtube_playlist_id == youtube_playlist_id)
            .where(PlaylistComparisonModel.local_folder_id == local_folder_id)
            .order_by(
                desc(PlaylistComparisonModel.compared_at),
                desc(PlaylistComparisonModel.id),
            )
        )
        model = self._session.scalars(statement).first()
        if model is None:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: PlaylistComparisonModel) -> PlaylistComparison:
        return PlaylistComparison(
            id=model.id,
            youtube_playlist_id=model.youtube_playlist_id,
            local_folder_id=model.local_folder_id,
            compared_at=model.compared_at,
            created_at=model.created_at,
        )
