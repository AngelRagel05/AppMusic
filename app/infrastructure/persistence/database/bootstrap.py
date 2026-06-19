from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import Engine, inspect, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.domain.metadata.services import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
)
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import IgnoredTerm

DEFAULT_IGNORED_TERMS: tuple[tuple[str, str, str], ...] = (
    ("official", "title", "global"),
    ("official video", "title", "global"),
    ("official audio", "title", "global"),
    ("official lyric video", "title", "global"),
    ("video", "title", "global"),
    ("audio", "title", "global"),
    ("lyrics", "title", "global"),
    ("lyric", "title", "global"),
    ("letras", "title", "global"),
    ("letra", "title", "global"),
    ("music video", "title", "global"),
    ("hd", "title", "global"),
    ("hq", "title", "global"),
    ("4k", "title", "global"),
    ("remastered", "title", "global"),
    ("visualizer", "title", "global"),
    ("visualiser", "title", "global"),
    ("audio oficial", "title", "global"),
    ("video oficial", "title", "global"),
    ("prod", "title", "global"),
    ("producido", "title", "global"),
)


class DatabaseBootstrapper:
    def __init__(self, engine: Engine, session_factory: sessionmaker[Session]) -> None:
        self._engine = engine
        self._session_factory = session_factory

    def bootstrap(self) -> None:
        Base.metadata.create_all(self._engine)
        self._apply_schema_compatibility()

        with self._session_factory() as session:
            self._seed_ignored_terms(session, DEFAULT_IGNORED_TERMS)
            session.commit()

    def _apply_schema_compatibility(self) -> None:
        inspector = inspect(self._engine)
        table_names = set(inspector.get_table_names())
        if "local_song" not in table_names:
            return

        localSongColumns = {column["name"] for column in inspector.get_columns("local_song")}
        playlistComparisonColumns = (
            {column["name"] for column in inspector.get_columns("playlist_comparison")}
            if "playlist_comparison" in table_names
            else set()
        )

        with self._engine.begin() as connection:
            if "is_available" not in localSongColumns:
                connection.execute(
                    text(
                        "ALTER TABLE local_song "
                        "ADD COLUMN is_available BOOLEAN NOT NULL DEFAULT TRUE"
                    )
                )
            if "normalized_title" not in localSongColumns:
                connection.execute(
                    text(
                        "ALTER TABLE local_song "
                        "ADD COLUMN normalized_title VARCHAR(255) NOT NULL DEFAULT ''"
                    )
                )
            if "normalized_artist" not in localSongColumns:
                connection.execute(
                    text(
                        "ALTER TABLE local_song "
                        "ADD COLUMN normalized_artist VARCHAR(255) NOT NULL DEFAULT ''"
                    )
                )
            if "youtube_playlist_imported_at" not in playlistComparisonColumns:
                connection.execute(
                    text(
                        "ALTER TABLE playlist_comparison "
                        "ADD COLUMN youtube_playlist_imported_at DATETIME NULL"
                    )
                )
            if "local_library_scanned_at" not in playlistComparisonColumns:
                connection.execute(
                    text(
                        "ALTER TABLE playlist_comparison "
                        "ADD COLUMN local_library_scanned_at DATETIME NULL"
                    )
                )
            if "ignored_terms_version" not in playlistComparisonColumns:
                connection.execute(
                    text(
                        "ALTER TABLE playlist_comparison "
                        "ADD COLUMN ignored_terms_version VARCHAR(128) NULL"
                    )
                )
            if "youtube_playlist_state_fingerprint" not in playlistComparisonColumns:
                connection.execute(
                    text(
                        "ALTER TABLE playlist_comparison "
                        "ADD COLUMN youtube_playlist_state_fingerprint VARCHAR(128) NULL"
                    )
                )
            if "local_library_state_fingerprint" not in playlistComparisonColumns:
                connection.execute(
                    text(
                        "ALTER TABLE playlist_comparison "
                        "ADD COLUMN local_library_state_fingerprint VARCHAR(128) NULL"
                    )
                )
            if "matching_rules_version" not in playlistComparisonColumns:
                connection.execute(
                    text(
                        "ALTER TABLE playlist_comparison "
                        "ADD COLUMN matching_rules_version VARCHAR(64) NULL"
                    )
                )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "ix_playlist_comparison_scope_compared_at "
                    "ON playlist_comparison "
                    "(youtube_playlist_id, local_folder_id, compared_at, id)"
                )
            )
            localSongRows = connection.execute(
                text(
                    "SELECT id, title, artist, normalized_title, normalized_artist "
                    "FROM local_song"
                )
            ).mappings()
            for row in localSongRows:
                normalizedTitle = row["normalized_title"] or normalizeMusicComparisonTitle(
                    row["title"] or ""
                )
                normalizedArtist = row["normalized_artist"] or normalizeMusicComparisonArtist(
                    row["artist"] or ""
                )
                if (
                    normalizedTitle == (row["normalized_title"] or "")
                    and normalizedArtist == (row["normalized_artist"] or "")
                ):
                    continue
                connection.execute(
                    text(
                        "UPDATE local_song "
                        "SET normalized_title = :normalized_title, "
                        "normalized_artist = :normalized_artist "
                        "WHERE id = :song_id"
                    ),
                    {
                        "normalized_title": normalizedTitle,
                        "normalized_artist": normalizedArtist,
                        "song_id": row["id"],
                    },
                )

    def _seed_ignored_terms(
        self,
        session: Session,
        ignored_terms: Iterable[tuple[str, str, str]],
    ) -> None:
        for term, scope, language in ignored_terms:
            existing_term = session.scalar(
                select(IgnoredTerm).where(
                    IgnoredTerm.term == term,
                    IgnoredTerm.scope == scope,
                    IgnoredTerm.language == language,
                )
            )
            if existing_term is not None:
                continue

            session.add(
                IgnoredTerm(
                    term=term,
                    scope=scope,
                    language=language,
                    is_active=True,
                )
            )
