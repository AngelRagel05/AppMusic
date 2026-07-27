"""Playlists domain services."""

from app.domain.playlists.services.artistComparisonValidationService import (
    classifyComparableArtistMatchForSelection,
)
from app.domain.playlists.services.matchDecisionSource import (
    AUTO_AMBIGUOUS,
    AUTO_NO_COMPETITIVE_CANDIDATE,
    AUTO_TITLE_ARTIST_DURATION,
    MANUAL_USER_LINKED_LOCAL_SONG,
    MANUAL_USER_MARKED_FOUND,
    MANUAL_USER_MARKED_MISSING,
    MANUAL_USER_MARKED_POSSIBLE,
    buildAutomaticMatchedBy,
    isAutomaticMatchedBy,
    isManualMatchedBy,
)
from app.domain.playlists.services.persistedComparisonContract import (
    ComparisonDependenciesFingerprint,
    ComparisonRefreshAction,
    ComparisonRefreshRequest,
    resolveComparisonRefreshAction,
    shouldInvalidatePersistedFoundMatch,
)
from app.domain.playlists.services.persistedComparisonModels import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
)
from app.domain.playlists.services.persistedPlaylistItemMatcherService import (
    PersistedPlaylistItemMatchResult,
    matchPersistedPlaylistItemToLocalSongs,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    ArtistMatchEvidence,
    CandidateMatchEvidence,
    CandidateScoreBreakdown,
    DurationMatchEvidence,
    TitleMatchEvidence,
    buildArtistMatchEvidence,
    buildCandidateMatchEvidence,
    buildDurationMatchEvidence,
    buildTextMatchEvidence,
)
from app.domain.playlists.services.sequentialLocalSongCandidateSelector import (
    ComparableLocalSongSequentialIndex,
    SequentialCandidateSelectionResult,
    buildComparableLocalSongSequentialIndex,
    selectSequentialLocalSongCandidates,
)
from app.domain.playlists.services.youtubePlaylistItemNormalizationService import (
    NormalizedYoutubePlaylistItemMetadata,
    normalizeYoutubePlaylistItemMetadata,
)

__all__ = [
    "AUTO_AMBIGUOUS",
    "AUTO_NO_COMPETITIVE_CANDIDATE",
    "AUTO_TITLE_ARTIST_DURATION",
    "MANUAL_USER_LINKED_LOCAL_SONG",
    "MANUAL_USER_MARKED_FOUND",
    "MANUAL_USER_MARKED_MISSING",
    "MANUAL_USER_MARKED_POSSIBLE",
    "ArtistMatchEvidence",
    "CandidateMatchEvidence",
    "CandidateScoreBreakdown",
    "ComparableLocalSong",
    "ComparableLocalSongSequentialIndex",
    "ComparableYoutubePlaylistItem",
    "ComparisonDependenciesFingerprint",
    "ComparisonRefreshAction",
    "ComparisonRefreshRequest",
    "DurationMatchEvidence",
    "NormalizedYoutubePlaylistItemMetadata",
    "PersistedPlaylistItemMatchResult",
    "SequentialCandidateSelectionResult",
    "TitleMatchEvidence",
    "buildArtistMatchEvidence",
    "buildAutomaticMatchedBy",
    "buildCandidateMatchEvidence",
    "buildComparableLocalSongSequentialIndex",
    "buildDurationMatchEvidence",
    "buildTextMatchEvidence",
    "classifyComparableArtistMatchForSelection",
    "isAutomaticMatchedBy",
    "isManualMatchedBy",
    "matchPersistedPlaylistItemToLocalSongs",
    "normalizeYoutubePlaylistItemMetadata",
    "resolveComparisonRefreshAction",
    "selectSequentialLocalSongCandidates",
    "shouldInvalidatePersistedFoundMatch",
]
