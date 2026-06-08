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
        statement = self._build_scope_statement(
            youtube_playlist_id,
            local_folder_id,
        )
        model = self._session.scalars(statement).first()
        if model is None:
            return None
        return self._to_entity(model)

    def list_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        limit: int,
    ) -> list[PlaylistComparison]:
        statement = self._build_scope_statement(
            youtube_playlist_id,
            local_folder_id,
        ).limit(limit)
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def _build_scope_statement(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> Select[tuple[PlaylistComparisonModel]]:
        return (
            select(PlaylistComparisonModel)
            .where(PlaylistComparisonModel.youtube_playlist_id == youtube_playlist_id)
            .where(PlaylistComparisonModel.local_folder_id == local_folder_id)
            .order_by(
                desc(PlaylistComparisonModel.compared_at),
                desc(PlaylistComparisonModel.id),
            )
        )

    def _to_entity(self, model: PlaylistComparisonModel) -> PlaylistComparison:
        return PlaylistComparison(
            id=model.id,
            youtube_playlist_id=model.youtube_playlist_id,
            local_folder_id=model.local_folder_id,
            compared_at=model.compared_at,
            created_at=model.created_at,
        )
