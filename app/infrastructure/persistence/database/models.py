from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class LocalFolder(TimestampMixin, Base):
    __tablename__ = "local_folder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    songs: Mapped[list[LocalSong]] = relationship(back_populates="local_folder")
    comparisons: Mapped[list[PlaylistComparison]] = relationship(back_populates="local_folder")
    downloads: Mapped[list[Download]] = relationship(back_populates="local_folder")


class YoutubePlaylist(TimestampMixin, Base):
    __tablename__ = "youtube_playlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    playlist_url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    external_playlist_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    items: Mapped[list[YoutubePlaylistItem]] = relationship(back_populates="youtube_playlist")
    comparisons: Mapped[list[PlaylistComparison]] = relationship(back_populates="youtube_playlist")


class YoutubePlaylistItem(TimestampMixin, Base):
    __tablename__ = "youtube_playlist_item"
    __table_args__ = (
        UniqueConstraint(
            "youtube_playlist_id",
            "external_video_id",
            name="uq_youtube_playlist_item_playlist_video",
        ),
        CheckConstraint("position > 0", name="ck_youtube_playlist_item_position_positive"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="ck_youtube_playlist_item_duration_seconds_non_negative",
        ),
        Index("ix_youtube_playlist_item_youtube_playlist_id", "youtube_playlist_id"),
        Index(
            "ix_youtube_playlist_item_playlist_position",
            "youtube_playlist_id",
            "position",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    youtube_playlist_id: Mapped[int] = mapped_column(
        ForeignKey("youtube_playlist.id"),
        nullable=False,
    )
    external_video_id: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_title: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_channel_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_artist: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    youtube_playlist: Mapped[YoutubePlaylist] = relationship(back_populates="items")
    comparison_results: Mapped[list[PlaylistComparisonResult]] = relationship(
        back_populates="youtube_playlist_item"
    )
    downloads: Mapped[list[Download]] = relationship(back_populates="youtube_playlist_item")


class Download(TimestampMixin, Base):
    __tablename__ = "download"
    __table_args__ = (
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_download_progress_percent_range",
        ),
        UniqueConstraint("task_id", name="uq_download_task_id"),
        Index("ix_download_youtube_playlist_item_id", "youtube_playlist_item_id"),
        Index("ix_download_local_folder_id", "local_folder_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    youtube_playlist_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("youtube_playlist_item.id"),
        nullable=True,
    )
    local_folder_id: Mapped[int] = mapped_column(ForeignKey("local_folder.id"), nullable=False)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_artist: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    target_file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    youtube_playlist_item: Mapped[YoutubePlaylistItem | None] = relationship(
        back_populates="downloads"
    )
    local_folder: Mapped[LocalFolder] = relationship(back_populates="downloads")
    local_song: Mapped[LocalSong | None] = relationship(back_populates="download", uselist=False)


class LocalSong(TimestampMixin, Base):
    __tablename__ = "local_song"
    __table_args__ = (
        CheckConstraint(
            "track_number_album >= 0",
            name="ck_local_song_track_number_album_non_negative",
        ),
        CheckConstraint(
            "duration_seconds >= 0",
            name="ck_local_song_duration_seconds_non_negative",
        ),
        Index("ix_local_song_local_folder_id", "local_folder_id"),
        Index("ix_local_song_download_id", "download_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    local_folder_id: Mapped[int] = mapped_column(ForeignKey("local_folder.id"), nullable=False)
    download_id: Mapped[int | None] = mapped_column(
        ForeignKey("download.id"),
        unique=True,
        nullable=True,
    )
    file_path: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    normalized_artist: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    album: Mapped[str] = mapped_column(String(255), nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    track_number_album: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)

    local_folder: Mapped[LocalFolder] = relationship(back_populates="songs")
    download: Mapped[Download | None] = relationship(back_populates="local_song")
    comparison_results: Mapped[list[PlaylistComparisonResult]] = relationship(
        back_populates="local_song"
    )


class PlaylistComparison(Base):
    __tablename__ = "playlist_comparison"
    __table_args__ = (
        Index("ix_playlist_comparison_youtube_playlist_id", "youtube_playlist_id"),
        Index("ix_playlist_comparison_local_folder_id", "local_folder_id"),
        Index(
            "ix_playlist_comparison_scope_compared_at",
            "youtube_playlist_id",
            "local_folder_id",
            "compared_at",
            "id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    youtube_playlist_id: Mapped[int] = mapped_column(
        ForeignKey("youtube_playlist.id"),
        nullable=False,
    )
    local_folder_id: Mapped[int] = mapped_column(ForeignKey("local_folder.id"), nullable=False)
    compared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    youtube_playlist_imported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    local_library_scanned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    youtube_playlist_state_fingerprint: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    local_library_state_fingerprint: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    ignored_terms_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    matching_rules_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    youtube_playlist: Mapped[YoutubePlaylist] = relationship(back_populates="comparisons")
    local_folder: Mapped[LocalFolder] = relationship(back_populates="comparisons")
    results: Mapped[list[PlaylistComparisonResult]] = relationship(
        back_populates="playlist_comparison"
    )


class PlaylistComparisonResult(TimestampMixin, Base):
    __tablename__ = "playlist_comparison_result"
    __table_args__ = (
        UniqueConstraint(
            "playlist_comparison_id",
            "youtube_playlist_item_id",
            name="uq_playlist_comparison_result_comparison_item",
        ),
        Index("ix_playlist_comparison_result_playlist_comparison_id", "playlist_comparison_id"),
        Index("ix_playlist_comparison_result_youtube_playlist_item_id", "youtube_playlist_item_id"),
        Index("ix_playlist_comparison_result_local_song_id", "local_song_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    playlist_comparison_id: Mapped[int] = mapped_column(
        ForeignKey("playlist_comparison.id"),
        nullable=False,
    )
    youtube_playlist_item_id: Mapped[int] = mapped_column(
        ForeignKey("youtube_playlist_item.id"),
        nullable=False,
    )
    local_song_id: Mapped[int | None] = mapped_column(ForeignKey("local_song.id"), nullable=True)
    match_status: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    playlist_comparison: Mapped[PlaylistComparison] = relationship(back_populates="results")
    youtube_playlist_item: Mapped[YoutubePlaylistItem] = relationship(
        back_populates="comparison_results"
    )
    local_song: Mapped[LocalSong | None] = relationship(back_populates="comparison_results")


class IgnoredTerm(TimestampMixin, Base):
    __tablename__ = "ignored_term"
    __table_args__ = (
        UniqueConstraint("term", "scope", "language", name="uq_ignored_term_term_scope_language"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    term: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(64), nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
