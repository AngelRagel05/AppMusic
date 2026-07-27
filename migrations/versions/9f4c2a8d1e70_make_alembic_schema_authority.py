"""make alembic the schema authority and extend downloads"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "9f4c2a8d1e70"
down_revision = "7b9f5f8c4a11"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    return {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _index_names(table_name: str) -> set[str]:
    return {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
        if index.get("name")
    }


def _unique_constraint_names(table_name: str) -> set[str]:
    return {
        constraint["name"]
        for constraint in sa.inspect(op.get_bind()).get_unique_constraints(table_name)
        if constraint.get("name")
    }


def upgrade() -> None:
    local_song_columns = _column_names("local_song")
    if "normalized_title" not in local_song_columns:
        op.add_column(
            "local_song",
            sa.Column(
                "normalized_title",
                sa.String(length=255),
                nullable=False,
                server_default="",
            ),
        )
    if "normalized_artist" not in local_song_columns:
        op.add_column(
            "local_song",
            sa.Column(
                "normalized_artist",
                sa.String(length=255),
                nullable=False,
                server_default="",
            ),
        )

    op.execute(
        sa.text(
            """
            UPDATE local_song
            SET normalized_title = lower(trim(title)),
                normalized_artist = lower(trim(artist))
            WHERE normalized_title = '' OR normalized_artist = ''
            """
        )
    )

    comparison_columns = _column_names("playlist_comparison")
    comparison_additions = (
        sa.Column("youtube_playlist_imported_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("local_library_scanned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "youtube_playlist_state_fingerprint",
            sa.String(length=128),
            nullable=True,
        ),
        sa.Column(
            "local_library_state_fingerprint",
            sa.String(length=128),
            nullable=True,
        ),
        sa.Column("ignored_terms_version", sa.String(length=128), nullable=True),
        sa.Column("matching_rules_version", sa.String(length=64), nullable=True),
    )
    for column in comparison_additions:
        if column.name not in comparison_columns:
            op.add_column("playlist_comparison", column)

    scope_index_name = "ix_playlist_comparison_scope_compared_at"
    if scope_index_name not in _index_names("playlist_comparison"):
        op.create_index(
            scope_index_name,
            "playlist_comparison",
            [
                "youtube_playlist_id",
                "local_folder_id",
                "compared_at",
                "id",
            ],
            unique=False,
        )

    download_columns = _column_names("download")
    download_additions = (
        sa.Column("task_id", sa.String(length=64), nullable=True),
        sa.Column("source_title", sa.String(length=512), nullable=True),
        sa.Column("source_artist", sa.String(length=255), nullable=True),
        sa.Column(
            "progress_percent",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )
    for column in download_additions:
        if column.name not in download_columns:
            op.add_column("download", column)

    op.execute(
        sa.text(
            """
            UPDATE download
            SET task_id = 'legacy-' || id
            WHERE task_id IS NULL OR task_id = ''
            """
        )
    )

    unique_names = _unique_constraint_names("download")
    with op.batch_alter_table("download") as batch_op:
        batch_op.alter_column(
            "youtube_playlist_item_id",
            existing_type=sa.Integer(),
            nullable=True,
        )
        batch_op.alter_column(
            "task_id",
            existing_type=sa.String(length=64),
            nullable=False,
        )
        batch_op.alter_column(
            "progress_percent",
            existing_type=sa.Float(),
            server_default=None,
        )
        if "uq_download_task_id" not in unique_names:
            batch_op.create_unique_constraint("uq_download_task_id", ["task_id"])
        batch_op.create_check_constraint(
            "ck_download_progress_percent_range",
            "progress_percent >= 0 AND progress_percent <= 100",
        )


def downgrade() -> None:
    with op.batch_alter_table("download") as batch_op:
        batch_op.drop_constraint(
            "ck_download_progress_percent_range",
            type_="check",
        )
        batch_op.drop_constraint("uq_download_task_id", type_="unique")
        batch_op.alter_column(
            "youtube_playlist_item_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.drop_column("progress_percent")
        batch_op.drop_column("source_artist")
        batch_op.drop_column("source_title")
        batch_op.drop_column("task_id")

    scope_index_name = "ix_playlist_comparison_scope_compared_at"
    if scope_index_name in _index_names("playlist_comparison"):
        op.drop_index(scope_index_name, table_name="playlist_comparison")

    for column_name in (
        "matching_rules_version",
        "ignored_terms_version",
        "local_library_state_fingerprint",
        "youtube_playlist_state_fingerprint",
        "local_library_scanned_at",
        "youtube_playlist_imported_at",
    ):
        if column_name in _column_names("playlist_comparison"):
            op.drop_column("playlist_comparison", column_name)

    local_song_columns = _column_names("local_song")
    if "normalized_artist" in local_song_columns:
        op.drop_column("local_song", "normalized_artist")
    if "normalized_title" in local_song_columns:
        op.drop_column("local_song", "normalized_title")
