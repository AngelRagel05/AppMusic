from __future__ import annotations

from alembic import command
from alembic.config import Config
from app.config.settings import PROJECT_ROOT, get_settings
from sqlalchemy import create_engine, inspect, text


def test_alembic_upgrades_an_empty_database_to_the_current_schema(
    tmp_path,
    monkeypatch,
) -> None:
    database_path = (tmp_path / "soundshelf.db").resolve()
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    try:
        command.upgrade(Config(str(PROJECT_ROOT / "alembic.ini")), "head")
    finally:
        get_settings.cache_clear()

    engine = create_engine(database_url)
    try:
        schema = inspect(engine)
        assert {
            "download",
            "ignored_term",
            "local_folder",
            "local_song",
            "playlist_comparison",
            "playlist_comparison_result",
            "youtube_playlist",
            "youtube_playlist_item",
        }.issubset(schema.get_table_names())
        assert {
            "normalized_title",
            "normalized_artist",
        }.issubset(
            {column["name"] for column in schema.get_columns("local_song")}
        )
        assert {
            "task_id",
            "source_title",
            "source_artist",
            "progress_percent",
        }.issubset(
            {column["name"] for column in schema.get_columns("download")}
        )
        with engine.connect() as connection:
            revision = connection.scalar(
                text("SELECT version_num FROM alembic_version")
            )
        assert revision == "9f4c2a8d1e70"
    finally:
        engine.dispose()
