from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path, PureWindowsPath

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "SoundShelf"
    app_env: str = "development"
    database_url: str = "sqlite:///music_app.db"
    log_level: str = "INFO"
    log_file: str | None = None
    data_directory: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "SOUNDSHELF_DATA_DIR",
            "DATA_DIRECTORY",
        ),
    )
    frontend_directory: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "SOUNDSHELF_FRONTEND_DIR",
            "FRONTEND_DIRECTORY",
        ),
    )
    music_folder: str | None = None
    download_folder: str | None = None
    ffmpeg_path: str = "ffmpeg"
    yt_dlp_timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0)
    temporary_folder: str = ".soundshelfTmp"
    api_host: str = "127.0.0.1"
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        validation_alias=AliasChoices("SOUNDSHELF_PORT", "API_PORT"),
    )
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    task_worker_count: int = Field(default=3, ge=1, le=8)
    task_poll_interval_ms: int = Field(default=1000, ge=250, le=10000)
    max_page_size: int = Field(default=100, ge=10, le=500)
    comparison_history_limit: int = Field(default=3, ge=1, le=20)

    @field_validator("database_url")
    @classmethod
    def resolveConfiguredDatabaseUrl(cls, value: str) -> str:
        return resolveDatabaseUrl(value)

    @property
    def corsOriginList(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def dataDirectoryPath(self) -> Path:
        configured_path = Path(self.data_directory or PROJECT_ROOT)
        if not configured_path.is_absolute():
            configured_path = PROJECT_ROOT / configured_path
        return configured_path.resolve(strict=False)

    @property
    def frontendDirectoryPath(self) -> Path | None:
        if not self.frontend_directory:
            return None
        configured_path = Path(self.frontend_directory)
        if not configured_path.is_absolute():
            configured_path = PROJECT_ROOT / configured_path
        return configured_path.resolve(strict=False)

    @property
    def logFilePath(self) -> Path | None:
        if not self.log_file:
            return None
        configured_path = Path(self.log_file)
        if not configured_path.is_absolute():
            configured_path = self.dataDirectoryPath / configured_path
        return configured_path.resolve(strict=False)

    @property
    def temporaryFolderPath(self) -> Path:
        configured_path = Path(self.temporary_folder)
        if not configured_path.is_absolute():
            configured_path = self.dataDirectoryPath / configured_path
        return configured_path.resolve(strict=False)


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
    return Settings()
