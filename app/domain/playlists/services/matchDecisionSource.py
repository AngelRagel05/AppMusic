from __future__ import annotations

from app.domain.playlists.services.playlistItemMatchingRules import CandidateMatchEvidence
from app.shared.constants.comparison import ComparisonStatus

AUTO_TITLE_ARTIST_DURATION = "auto:title_artist_duration"
AUTO_AMBIGUOUS = "auto:ambiguous"
AUTO_NO_COMPETITIVE_CANDIDATE = "auto:no_competitive_candidate"

MANUAL_USER_LINKED_LOCAL_SONG = "manual:user_linked_local_song"
MANUAL_USER_MARKED_FOUND = "manual:user_marked_found"
MANUAL_USER_MARKED_MISSING = "manual:user_marked_missing"
MANUAL_USER_MARKED_POSSIBLE = "manual:user_marked_possible"


def buildAutomaticMatchedBy(
    *,
    status: ComparisonStatus,
    evidence: CandidateMatchEvidence,
) -> str:
    if status is ComparisonStatus.FOUND:
        return AUTO_TITLE_ARTIST_DURATION
    if evidence.ambiguity_count > 1:
        return AUTO_AMBIGUOUS
    return AUTO_NO_COMPETITIVE_CANDIDATE


def isAutomaticMatchedBy(value: str | None) -> bool:
    return (value or "").startswith("auto:")


def isManualMatchedBy(value: str | None) -> bool:
    return (value or "").startswith("manual:")
