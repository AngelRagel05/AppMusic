from __future__ import annotations

from music_app.app.infrastructure.database.base import Base
from music_app.app.infrastructure.database.models import SongModel  # noqa: F401
from music_app.app.infrastructure.database.session import engine


def bootstrap_database() -> None:
    # Keeps first run simple while Alembic remains the canonical migration mechanism.
    Base.metadata.create_all(bind=engine)

