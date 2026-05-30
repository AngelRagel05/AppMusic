"""Domain services and repository contracts."""

from app.domain.services.base_repository import BaseRepository
from app.domain.services.ignored_term_repository import IgnoredTermRepository

__all__ = ["BaseRepository", "IgnoredTermRepository"]
