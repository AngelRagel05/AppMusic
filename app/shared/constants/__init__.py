"""Shared constants."""

from app.shared.constants.comparison import ComparisonStatus
from app.shared.constants.ignoredTerms import LANGUAGE_OPTIONS, SCOPE_OPTIONS
from app.shared.constants.youtube import (
    CANONICAL_YOUTUBE_PLAYLIST_URL,
    VALID_YOUTUBE_HOSTS,
)

__all__ = [
    "CANONICAL_YOUTUBE_PLAYLIST_URL",
    "LANGUAGE_OPTIONS",
    "SCOPE_OPTIONS",
    "VALID_YOUTUBE_HOSTS",
    "ComparisonStatus",
]
