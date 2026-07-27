from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from fastapi import Request
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.persistence.repositories import (
    DownloadSqlAlchemyRepository,
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
    PlaylistComparisonResultSqlAlchemyRepository,
    PlaylistComparisonSqlAlchemyRepository,
    YoutubePlaylistItemSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.infrastructure.tasks import LocalTaskManager


@dataclass(frozen=True, slots=True)
class ApiRepositoryRegistry:
    session: Session
    downloadRepository: DownloadSqlAlchemyRepository
    ignoredTermRepository: IgnoredTermSqlAlchemyRepository
    localFolderRepository: LocalFolderSqlAlchemyRepository
    localSongRepository: LocalSongSqlAlchemyRepository
    playlistComparisonRepository: PlaylistComparisonSqlAlchemyRepository
    playlistComparisonResultRepository: PlaylistComparisonResultSqlAlchemyRepository
    youtubePlaylistItemRepository: YoutubePlaylistItemSqlAlchemyRepository
    youtubePlaylistRepository: YoutubePlaylistSqlAlchemyRepository


def createApiRepositoryRegistry(session: Session) -> ApiRepositoryRegistry:
    return ApiRepositoryRegistry(
        session=session,
        downloadRepository=DownloadSqlAlchemyRepository(session),
        ignoredTermRepository=IgnoredTermSqlAlchemyRepository(session),
        localFolderRepository=LocalFolderSqlAlchemyRepository(session),
        localSongRepository=LocalSongSqlAlchemyRepository(session),
        playlistComparisonRepository=PlaylistComparisonSqlAlchemyRepository(session),
        playlistComparisonResultRepository=PlaylistComparisonResultSqlAlchemyRepository(
            session
        ),
        youtubePlaylistItemRepository=YoutubePlaylistItemSqlAlchemyRepository(session),
        youtubePlaylistRepository=YoutubePlaylistSqlAlchemyRepository(session),
    )


def getSessionFactory(request: Request) -> sessionmaker[Session]:
    return request.app.state.sessionFactory


def getSession(request: Request) -> Generator[Session, None, None]:
    session_factory = getSessionFactory(request)
    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def getRegistry(session: Session) -> ApiRepositoryRegistry:
    return createApiRepositoryRegistry(session)


def getTaskManager(request: Request) -> LocalTaskManager:
    return request.app.state.taskManager
