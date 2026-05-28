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
    music_scan_path: str | None
    ffmpeg_binary: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Music App"),
        app_env=os.getenv("APP_ENV", "development"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///music_app.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        music_scan_path=os.getenv("MUSIC_SCAN_PATH") or None,
        ffmpeg_binary=os.getenv("FFMPEG_BINARY", "ffmpeg"),
    )

