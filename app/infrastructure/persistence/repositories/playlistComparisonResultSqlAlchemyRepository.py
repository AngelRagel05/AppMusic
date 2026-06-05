from __future__ import annotations

from sqlalchemy import Select, select

from app.domain.playlists.entities.playlistComparisonResult import (
    PlaylistComparisonResult,
)
from app.domain.playlists.repositories.playlistComparisonResultRepository import (
    PlaylistComparisonResultRepository,
)
from app.infrastructure.persistence.database.models import (
    PlaylistComparisonResult as PlaylistComparisonResultModel,
)


class PlaylistComparisonResultSqlAlchemyRepository(PlaylistComparisonResultRepository):
    def __init__(self, session) -> None:
        self._session = session

    def save_for_comparison(
        self,
        playlist_comparison_id: int,
        results: list[PlaylistComparisonResult],
    ) -> list[PlaylistComparisonResult]:
        for result in results:
            self._session.add(
                PlaylistComparisonResultModel(
                    playlist_comparison_id=playlist_comparison_id,
                    youtube_playlist_item_id=result.youtube_playlist_item_id,
                    local_song_id=result.local_song_id,
                    match_status=result.match_status,
                    score=result.score,
                    matched_by=result.matched_by,
                )
            )

        self._session.commit()
        return self.list_by_comparison(playlist_comparison_id)

    def list_by_comparison(
        self,
        playlist_comparison_id: int,
    ) -> list[PlaylistComparisonResult]:
        statement: Select[tuple[PlaylistComparisonResultModel]] = (
            select(PlaylistComparisonResultModel)
            .where(PlaylistComparisonResultModel.playlist_comparison_id == playlist_comparison_id)
            .order_by(PlaylistComparisonResultModel.youtube_playlist_item_id.asc())
        )
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def _to_entity(
        self,
        model: PlaylistComparisonResultModel,
    ) -> PlaylistComparisonResult:
        return PlaylistComparisonResult(
            id=model.id,
            playlist_comparison_id=model.playlist_comparison_id,
            youtube_playlist_item_id=model.youtube_playlist_item_id,
            local_song_id=model.local_song_id,
            match_status=model.match_status,
            score=model.score,
            matched_by=model.matched_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
