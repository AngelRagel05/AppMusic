from __future__ import annotations

from app.infrastructure.persistence.database.bootstrap import (
    DEFAULT_IGNORED_TERMS,
    DatabaseBootstrapper,
)
from app.infrastructure.persistence.database.models import IgnoredTerm
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session, sessionmaker


def create_bootstrapper() -> tuple[DatabaseBootstrapper, sessionmaker[Session]]:
    engine = create_engine("sqlite:///:memory:", future=True)
    session_factory = sessionmaker(bind=engine, class_=Session)
    return DatabaseBootstrapper(engine, session_factory), session_factory


def test_bootstrap_creates_tables_and_seeds_default_ignored_terms() -> None:
    bootstrapper, session_factory = create_bootstrapper()

    bootstrapper.bootstrap()

    inspector = inspect(session_factory.kw["bind"])
    assert "ignored_term" in inspector.get_table_names()

    with session_factory() as session:
        persisted_terms = session.scalars(select(IgnoredTerm)).all()

    assert len(persisted_terms) == len(DEFAULT_IGNORED_TERMS)


def test_bootstrap_is_idempotent_for_default_ignored_terms() -> None:
    bootstrapper, session_factory = create_bootstrapper()

    bootstrapper.bootstrap()
    bootstrapper.bootstrap()

    with session_factory() as session:
        persisted_terms = session.scalars(select(IgnoredTerm)).all()

    assert len(persisted_terms) == len(DEFAULT_IGNORED_TERMS)


def test_bootstrap_adds_local_song_availability_column_for_legacy_schema() -> None:
    bootstrapper, session_factory = create_bootstrapper()
    engine = session_factory.kw["bind"]
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE local_song (
                    id INTEGER NOT NULL PRIMARY KEY,
                    local_folder_id INTEGER NOT NULL,
                    download_id INTEGER,
                    file_path VARCHAR(1024) NOT NULL UNIQUE,
                    file_name VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    artist VARCHAR(255) NOT NULL,
                    album VARCHAR(255) NOT NULL,
                    release_year INTEGER NOT NULL,
                    track_number_album INTEGER NOT NULL,
                    duration_seconds FLOAT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        )

    bootstrapper.bootstrap()

    inspector = inspect(engine)
    local_song_columns = {column["name"] for column in inspector.get_columns("local_song")}

    assert "is_available" in local_song_columns
