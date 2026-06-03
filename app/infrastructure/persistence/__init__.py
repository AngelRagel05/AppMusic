"""Persistence infrastructure."""

from app.infrastructure.persistence.database import (
    Base,
    DatabaseBootstrapper,
    Download,
    IgnoredTerm,
    LocalFolder,
    LocalSong,
    PlaylistComparison,
    PlaylistComparisonResult,
    SessionLocal,
    YoutubePlaylist,
    YoutubePlaylistItem,
    engine,
    get_session,
)
from app.infrastructure.persistence.repositories import (
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    SqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)

__all__ = [
    "Base",
    "DatabaseBootstrapper",
    "Download",
    "IgnoredTerm",
    "IgnoredTermSqlAlchemyRepository",
    "LocalFolder",
    "LocalFolderSqlAlchemyRepository",
    "LocalSong",
    "PlaylistComparison",
    "PlaylistComparisonResult",
    "SessionLocal",
    "SqlAlchemyRepository",
    "YoutubePlaylist",
    "YoutubePlaylistItem",
    "YoutubePlaylistSqlAlchemyRepository",
    "engine",
    "get_session",
]
