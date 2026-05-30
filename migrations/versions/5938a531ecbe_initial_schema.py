"""initial schema"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "5938a531ecbe"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ignored_term",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=255), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "term",
            "scope",
            "language",
            name="uq_ignored_term_term_scope_language",
        ),
    )
    op.create_table(
        "local_folder",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=1024), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path"),
    )
    op.create_table(
        "youtube_playlist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("playlist_url", sa.String(length=2048), nullable=False),
        sa.Column("external_playlist_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_playlist_id"),
        sa.UniqueConstraint("playlist_url"),
    )
    op.create_table(
        "playlist_comparison",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("youtube_playlist_id", sa.Integer(), nullable=False),
        sa.Column("local_folder_id", sa.Integer(), nullable=False),
        sa.Column("compared_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["local_folder_id"], ["local_folder.id"]),
        sa.ForeignKeyConstraint(["youtube_playlist_id"], ["youtube_playlist.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_playlist_comparison_local_folder_id",
        "playlist_comparison",
        ["local_folder_id"],
        unique=False,
    )
    op.create_index(
        "ix_playlist_comparison_youtube_playlist_id",
        "playlist_comparison",
        ["youtube_playlist_id"],
        unique=False,
    )
    op.create_table(
        "youtube_playlist_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("youtube_playlist_id", sa.Integer(), nullable=False),
        sa.Column("video_id", sa.String(length=255), nullable=False),
        sa.Column("video_url", sa.String(length=2048), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("artist", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("position > 0", name="ck_youtube_playlist_item_position_positive"),
        sa.ForeignKeyConstraint(["youtube_playlist_id"], ["youtube_playlist.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("video_id"),
        sa.UniqueConstraint("video_url"),
        sa.UniqueConstraint(
            "youtube_playlist_id",
            "position",
            name="uq_youtube_playlist_item_playlist_position",
        ),
    )
    op.create_index(
        "ix_youtube_playlist_item_youtube_playlist_id",
        "youtube_playlist_item",
        ["youtube_playlist_id"],
        unique=False,
    )
    op.create_table(
        "download",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("youtube_playlist_item_id", sa.Integer(), nullable=False),
        sa.Column("local_folder_id", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("target_file_path", sa.String(length=1024), nullable=True),
        sa.Column("error_message", sa.String(length=2048), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["local_folder_id"], ["local_folder.id"]),
        sa.ForeignKeyConstraint(["youtube_playlist_item_id"], ["youtube_playlist_item.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_download_local_folder_id", "download", ["local_folder_id"], unique=False)
    op.create_index(
        "ix_download_youtube_playlist_item_id",
        "download",
        ["youtube_playlist_item_id"],
        unique=False,
    )
    op.create_table(
        "local_song",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("local_folder_id", sa.Integer(), nullable=False),
        sa.Column("download_id", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("artist", sa.String(length=255), nullable=False),
        sa.Column("album", sa.String(length=255), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=False),
        sa.Column("track_number_album", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "duration_seconds >= 0",
            name="ck_local_song_duration_seconds_non_negative",
        ),
        sa.CheckConstraint(
            "track_number_album >= 0",
            name="ck_local_song_track_number_album_non_negative",
        ),
        sa.ForeignKeyConstraint(["download_id"], ["download.id"]),
        sa.ForeignKeyConstraint(["local_folder_id"], ["local_folder.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("download_id"),
        sa.UniqueConstraint("file_path"),
    )
    op.create_index("ix_local_song_download_id", "local_song", ["download_id"], unique=False)
    op.create_index(
        "ix_local_song_local_folder_id",
        "local_song",
        ["local_folder_id"],
        unique=False,
    )
    op.create_table(
        "playlist_comparison_result",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("playlist_comparison_id", sa.Integer(), nullable=False),
        sa.Column("youtube_playlist_item_id", sa.Integer(), nullable=False),
        sa.Column("local_song_id", sa.Integer(), nullable=True),
        sa.Column("match_status", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("matched_by", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["local_song_id"], ["local_song.id"]),
        sa.ForeignKeyConstraint(["playlist_comparison_id"], ["playlist_comparison.id"]),
        sa.ForeignKeyConstraint(["youtube_playlist_item_id"], ["youtube_playlist_item.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "playlist_comparison_id",
            "youtube_playlist_item_id",
            name="uq_playlist_comparison_result_comparison_item",
        ),
    )
    op.create_index(
        "ix_playlist_comparison_result_local_song_id",
        "playlist_comparison_result",
        ["local_song_id"],
        unique=False,
    )
    op.create_index(
        "ix_playlist_comparison_result_playlist_comparison_id",
        "playlist_comparison_result",
        ["playlist_comparison_id"],
        unique=False,
    )
    op.create_index(
        "ix_playlist_comparison_result_youtube_playlist_item_id",
        "playlist_comparison_result",
        ["youtube_playlist_item_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_playlist_comparison_result_youtube_playlist_item_id",
        table_name="playlist_comparison_result",
    )
    op.drop_index(
        "ix_playlist_comparison_result_playlist_comparison_id",
        table_name="playlist_comparison_result",
    )
    op.drop_index(
        "ix_playlist_comparison_result_local_song_id",
        table_name="playlist_comparison_result",
    )
    op.drop_table("playlist_comparison_result")
    op.drop_index("ix_local_song_local_folder_id", table_name="local_song")
    op.drop_index("ix_local_song_download_id", table_name="local_song")
    op.drop_table("local_song")
    op.drop_index("ix_download_youtube_playlist_item_id", table_name="download")
    op.drop_index("ix_download_local_folder_id", table_name="download")
    op.drop_table("download")
    op.drop_index(
        "ix_youtube_playlist_item_youtube_playlist_id",
        table_name="youtube_playlist_item",
    )
    op.drop_table("youtube_playlist_item")
    op.drop_index(
        "ix_playlist_comparison_youtube_playlist_id",
        table_name="playlist_comparison",
    )
    op.drop_index(
        "ix_playlist_comparison_local_folder_id",
        table_name="playlist_comparison",
    )
    op.drop_table("playlist_comparison")
    op.drop_table("youtube_playlist")
    op.drop_table("local_folder")
    op.drop_table("ignored_term")
