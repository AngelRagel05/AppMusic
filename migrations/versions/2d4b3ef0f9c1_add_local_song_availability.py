"""add local song availability"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "2d4b3ef0f9c1"
down_revision = "5938a531ecbe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "local_song",
        sa.Column(
            "is_available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("local_song", "is_available")
