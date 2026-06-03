from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.use_cases import BootstrapDatabaseUseCase
from app.infrastructure.persistence import (
    DatabaseBootstrapper,
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    SessionLocal,
    YoutubePlaylistSqlAlchemyRepository,
    engine,
    get_session,
)


@dataclass(frozen=True)
class PersistenceRegistry:
    session: Session
    ignoredTermRepository: IgnoredTermSqlAlchemyRepository
    localFolderRepository: LocalFolderSqlAlchemyRepository
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
            youtubePlaylistRepository=YoutubePlaylistSqlAlchemyRepository(session),
        )
