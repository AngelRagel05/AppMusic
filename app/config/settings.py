from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    app_env: str
    database_url: str
    log_level: str
    music_folder: str | None
    download_folder: str | None
    ffmpeg_path: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Music App"),
        app_env=os.getenv("APP_ENV", "development"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///music_app.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        music_folder=os.getenv("MUSIC_FOLDER") or None,
        download_folder=os.getenv("DOWNLOAD_FOLDER") or None,
        ffmpeg_path=os.getenv("FFMPEG_PATH", "ffmpeg"),
    )
