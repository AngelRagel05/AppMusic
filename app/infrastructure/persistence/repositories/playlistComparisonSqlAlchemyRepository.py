from __future__ import annotations

from datetime import UTC, datetime

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

    def find_by_id(
        self,
        playlist_comparison_id: int,
    ) -> PlaylistComparison | None:
        model = self._session.get(PlaylistComparisonModel, playlist_comparison_id)
        if model is None:
            return None
        return self._to_entity(model)

    def create(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        youtube_playlist_imported_at=None,
        local_library_scanned_at=None,
        youtube_playlist_state_fingerprint: str | None = None,
        local_library_state_fingerprint: str | None = None,
        ignored_terms_version: str | None = None,
        matching_rules_version: str | None = None,
    ) -> PlaylistComparison:
        model = PlaylistComparisonModel(
            youtube_playlist_id=youtube_playlist_id,
            local_folder_id=local_folder_id,
            youtube_playlist_imported_at=youtube_playlist_imported_at,
            local_library_scanned_at=local_library_scanned_at,
            youtube_playlist_state_fingerprint=youtube_playlist_state_fingerprint,
            local_library_state_fingerprint=local_library_state_fingerprint,
            ignored_terms_version=ignored_terms_version,
            matching_rules_version=matching_rules_version,
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

    def list_excess_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        keep_latest: int,
    ) -> list[PlaylistComparison]:
        if keep_latest < 0:
            msg = "keep_latest no puede ser negativo."
            raise ValueError(msg)

        statement = self._build_scope_statement(
            youtube_playlist_id,
            local_folder_id,
        ).offset(keep_latest)
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def delete_by_ids(
        self,
        playlist_comparison_ids: list[int],
    ) -> None:
        if not playlist_comparison_ids:
            return

        (
            self._session.query(PlaylistComparisonModel)
            .filter(PlaylistComparisonModel.id.in_(playlist_comparison_ids))
            .delete(synchronize_session=False)
        )
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()

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
            compared_at=self._normalizeTimestamp(model.compared_at),
            youtube_playlist_imported_at=self._normalizeTimestamp(
                model.youtube_playlist_imported_at
            ),
            local_library_scanned_at=self._normalizeTimestamp(
                model.local_library_scanned_at
            ),
            youtube_playlist_state_fingerprint=model.youtube_playlist_state_fingerprint,
            local_library_state_fingerprint=model.local_library_state_fingerprint,
            ignored_terms_version=model.ignored_terms_version,
            matching_rules_version=model.matching_rules_version,
            created_at=self._normalizeTimestamp(model.created_at),
        )

    def _normalizeTimestamp(self, timestamp: datetime | None) -> datetime | None:
        if timestamp is None:
            return None
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=UTC)
        return timestamp.astimezone(UTC)
