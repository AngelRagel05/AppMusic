"""Playlists domain services."""

from app.domain.playlists.services.playlistItemMatcherService import (
    PlaylistItemMatchResult,
    matchYoutubePlaylistItemToLocalSongs,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET,
    DurationMatchThresholds,
    MatchClassificationThresholds,
    PlaylistItemMatchingRuleset,
    TextMatchWeights,
    buildMatchReason,
    classifyMatchStatus,
    normalizedSimilarityRatio,
    scoreDuration,
    scoreNormalizedText,
)
from app.domain.playlists.services.youtubePlaylistItemNormalizationService import (
    NormalizedYoutubePlaylistItemMetadata,
    normalizeYoutubePlaylistItemMetadata,
)

__all__ = [
    "DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET",
    "DurationMatchThresholds",
    "MatchClassificationThresholds",
    "PlaylistItemMatchResult",
    "PlaylistItemMatchingRuleset",
    "NormalizedYoutubePlaylistItemMetadata",
    "TextMatchWeights",
    "buildMatchReason",
    "classifyMatchStatus",
    "matchYoutubePlaylistItemToLocalSongs",
    "normalizedSimilarityRatio",
    "normalizeYoutubePlaylistItemMetadata",
    "scoreDuration",
    "scoreNormalizedText",
]
