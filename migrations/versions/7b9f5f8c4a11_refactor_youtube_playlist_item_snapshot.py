"""refactor youtube playlist item snapshot"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "7b9f5f8c4a11"
down_revision = "2d4b3ef0f9c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    naming_convention = {"uq": "uq_%(table_name)s_%(column_0_name)s"}

    with op.batch_alter_table(
        "youtube_playlist_item",
        naming_convention=naming_convention,
    ) as batch_op:
        batch_op.drop_constraint(
            "uq_youtube_playlist_item_playlist_position",
            type_="unique",
        )
        batch_op.drop_constraint("uq_youtube_playlist_item_video_id", type_="unique")
        batch_op.drop_constraint("uq_youtube_playlist_item_video_url", type_="unique")
        batch_op.drop_column("video_url")
        batch_op.drop_column("release_year")
        batch_op.alter_column("video_id", new_column_name="external_video_id")
        batch_op.alter_column(
            "title",
            new_column_name="raw_title",
            existing_type=sa.String(length=255),
            type_=sa.String(length=512),
        )
        batch_op.alter_column("artist", new_column_name="raw_channel_name", existing_type=sa.String(length=255))
        batch_op.add_column(
            sa.Column("normalized_title", sa.String(length=512), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("normalized_artist", sa.String(length=255), nullable=False, server_default="")
        )
        batch_op.add_column(sa.Column("duration_seconds", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_unique_constraint(
            "uq_youtube_playlist_item_playlist_video",
            ["youtube_playlist_id", "external_video_id"],
        )
        batch_op.create_check_constraint(
            "ck_youtube_playlist_item_duration_seconds_non_negative",
            "duration_seconds IS NULL OR duration_seconds >= 0",
        )
        batch_op.create_index(
            "ix_youtube_playlist_item_playlist_position",
            ["youtube_playlist_id", "position"],
            unique=False,
        )

    op.execute(
        sa.text(
            """
            UPDATE youtube_playlist_item
            SET normalized_title = raw_title,
                normalized_artist = raw_channel_name
            """
        )
    )

    with op.batch_alter_table("youtube_playlist_item") as batch_op:
        batch_op.alter_column("normalized_title", server_default=None)
        batch_op.alter_column("normalized_artist", server_default=None)


def downgrade() -> None:
    naming_convention = {"uq": "uq_%(table_name)s_%(column_0_name)s"}

    with op.batch_alter_table(
        "youtube_playlist_item",
        naming_convention=naming_convention,
    ) as batch_op:
        batch_op.drop_index("ix_youtube_playlist_item_playlist_position")
        batch_op.drop_constraint(
            "ck_youtube_playlist_item_duration_seconds_non_negative",
            type_="check",
        )
        batch_op.drop_constraint(
            "uq_youtube_playlist_item_playlist_video",
            type_="unique",
        )
        batch_op.drop_column("published_at")
        batch_op.drop_column("duration_seconds")
        batch_op.drop_column("normalized_artist")
        batch_op.drop_column("normalized_title")
        batch_op.alter_column(
            "raw_channel_name",
            new_column_name="artist",
            existing_type=sa.String(length=255),
        )
        batch_op.alter_column(
            "raw_title",
            new_column_name="title",
            existing_type=sa.String(length=512),
            type_=sa.String(length=255),
        )
        batch_op.alter_column(
            "external_video_id",
            new_column_name="video_id",
            existing_type=sa.String(length=255),
        )
        batch_op.add_column(
            sa.Column("release_year", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("video_url", sa.String(length=2048), nullable=False, server_default="")
        )
        batch_op.create_unique_constraint(
            "uq_youtube_playlist_item_video_id",
            ["video_id"],
        )
        batch_op.create_unique_constraint(
            "uq_youtube_playlist_item_video_url",
            ["video_url"],
        )
        batch_op.create_unique_constraint(
            "uq_youtube_playlist_item_playlist_position",
            ["youtube_playlist_id", "position"],
        )

    op.execute(
        sa.text(
            """
            UPDATE youtube_playlist_item
            SET video_url = '',
                release_year = 0
            """
        )
    )

    with op.batch_alter_table("youtube_playlist_item") as batch_op:
        batch_op.alter_column("video_url", server_default=None)
        batch_op.alter_column("release_year", server_default=None)
