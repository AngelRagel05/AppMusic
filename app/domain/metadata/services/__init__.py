"""Metadata domain services."""

from app.domain.metadata.services.musicComparisonNormalizationService import (
    COMPARISON_IGNORED_TERMS,
    NormalizedComparisonTextParts,
    NormalizedMusicComparisonMetadata,
    normalizeMusicComparisonAlbum,
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
    normalizeMusicComparisonTitle,
    splitMusicComparisonSegments,
)

__all__ = [
    "COMPARISON_IGNORED_TERMS",
    "NormalizedComparisonTextParts",
    "NormalizedMusicComparisonMetadata",
    "normalizeMusicComparisonAlbum",
    "normalizeMusicComparisonArtist",
    "normalizeMusicComparisonMetadata",
    "normalizeMusicComparisonText",
    "normalizeMusicComparisonTitle",
    "splitMusicComparisonSegments",
]
