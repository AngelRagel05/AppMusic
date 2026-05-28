"""create songs table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_create_songs_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "songs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("path", sa.String(length=1024), nullable=False, unique=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("artist", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("album", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("track_number", sa.Integer(), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_songs_title", "songs", ["title"])
    op.create_index("ix_songs_artist", "songs", ["artist"])


def downgrade() -> None:
    op.drop_index("ix_songs_artist", table_name="songs")
    op.drop_index("ix_songs_title", table_name="songs")
    op.drop_table("songs")

