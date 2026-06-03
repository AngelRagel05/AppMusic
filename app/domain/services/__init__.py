"""Domain services and repository contracts."""

from app.domain.services.base_repository import BaseRepository
from app.domain.services.ignoredTermRepository import IgnoredTermRepository

__all__ = ["BaseRepository", "IgnoredTermRepository"]
