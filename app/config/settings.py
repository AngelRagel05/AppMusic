from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PureWindowsPath

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    app_env: str
    database_url: str
    log_level: str
    music_folder: str | None
    download_folder: str | None
    ffmpeg_path: str


def resolveDatabaseUrl(database_url: str) -> str:
    normalized_database_url = (database_url or "").strip()
    if not normalized_database_url.startswith("sqlite:///"):
        return normalized_database_url

    sqlite_path = normalized_database_url.removeprefix("sqlite:///")
    if not sqlite_path or _isAbsoluteSqlitePath(sqlite_path):
        return normalized_database_url

    resolved_database_path = (PROJECT_ROOT / sqlite_path).resolve()
    return f"sqlite:///{resolved_database_path.as_posix()}"


def _isAbsoluteSqlitePath(sqlite_path: str) -> bool:
    normalized_path = sqlite_path.strip()
    if not normalized_path:
        return False
    if Path(normalized_path).is_absolute():
        return True
    if PureWindowsPath(normalized_path).is_absolute():
        return True
    return re.match(r"^[A-Za-z]:[\\/]", normalized_path) is not None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Music App"),
        app_env=os.getenv("APP_ENV", "development"),
        database_url=resolveDatabaseUrl(
            os.getenv("DATABASE_URL", "sqlite:///music_app.db")
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        music_folder=os.getenv("MUSIC_FOLDER") or None,
        download_folder=os.getenv("DOWNLOAD_FOLDER") or None,
        ffmpeg_path=os.getenv("FFMPEG_PATH", "ffmpeg"),
    )
