"""Metadata domain services."""

from app.domain.metadata.services.musicComparisonNormalizationService import (
    COMPARISON_IGNORED_TERMS,
    IgnoredTermsByScope,
    NormalizedComparisonTextParts,
    NormalizedMusicComparisonMetadata,
    normalizeMusicComparisonAlbum,
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonArtistParts,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
    normalizeMusicComparisonTitle,
    splitMusicComparisonSegments,
)

__all__ = [
    "COMPARISON_IGNORED_TERMS",
    "IgnoredTermsByScope",
    "NormalizedComparisonTextParts",
    "NormalizedMusicComparisonMetadata",
    "normalizeMusicComparisonAlbum",
    "normalizeMusicComparisonArtist",
    "normalizeMusicComparisonArtistParts",
    "normalizeMusicComparisonMetadata",
    "normalizeMusicComparisonText",
    "normalizeMusicComparisonTitle",
    "splitMusicComparisonSegments",
]
