from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.use_cases import BootstrapDatabaseUseCase
from app.infrastructure.persistence import (
    DatabaseBootstrapper,
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
    PlaylistComparisonResultSqlAlchemyRepository,
    PlaylistComparisonSqlAlchemyRepository,
    SessionLocal,
    YoutubePlaylistItemSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
    engine,
    get_session,
)


@dataclass(frozen=True)
class PersistenceRegistry:
    session: Session
    ignoredTermRepository: IgnoredTermSqlAlchemyRepository
    localFolderRepository: LocalFolderSqlAlchemyRepository
    localSongRepository: LocalSongSqlAlchemyRepository
    playlistComparisonRepository: PlaylistComparisonSqlAlchemyRepository
    playlistComparisonResultRepository: PlaylistComparisonResultSqlAlchemyRepository
    youtubePlaylistItemRepository: YoutubePlaylistItemSqlAlchemyRepository
    youtubePlaylistRepository: YoutubePlaylistSqlAlchemyRepository


class PersistenceFactory:
    def bootstrapDatabase(self) -> None:
        BootstrapDatabaseUseCase(DatabaseBootstrapper(engine, SessionLocal)).execute()

    def createRegistry(self) -> PersistenceRegistry:
        session = get_session()
        return PersistenceRegistry(
            session=session,
            ignoredTermRepository=IgnoredTermSqlAlchemyRepository(session),
            localFolderRepository=LocalFolderSqlAlchemyRepository(session),
            localSongRepository=LocalSongSqlAlchemyRepository(session),
            playlistComparisonRepository=PlaylistComparisonSqlAlchemyRepository(session),
            playlistComparisonResultRepository=PlaylistComparisonResultSqlAlchemyRepository(
                session
            ),
            youtubePlaylistItemRepository=YoutubePlaylistItemSqlAlchemyRepository(
                session
            ),
            youtubePlaylistRepository=YoutubePlaylistSqlAlchemyRepository(session),
        )
