from __future__ import annotations

from pathlib import Path

from app.config.settings import PROJECT_ROOT, resolveDatabaseUrl


def test_resolve_database_url_returns_absolute_sqlite_path_from_project_root() -> None:
    resolved_url = resolveDatabaseUrl("sqlite:///music_app.db")

    expected_path = (PROJECT_ROOT / "music_app.db").resolve().as_posix()
    assert resolved_url == f"sqlite:///{expected_path}"


def test_resolve_database_url_keeps_absolute_sqlite_path_unchanged() -> None:
    absolute_path = Path("C:/tmp/music_app.db")

    resolved_url = resolveDatabaseUrl(f"sqlite:///{absolute_path.as_posix()}")

    assert resolved_url == f"sqlite:///{absolute_path.as_posix()}"


def test_resolve_database_url_keeps_non_sqlite_database_urls_unchanged() -> None:
    database_url = "postgresql://user:pass@localhost/music_app"

    assert resolveDatabaseUrl(database_url) == database_url
