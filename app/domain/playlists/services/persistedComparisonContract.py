from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ComparisonRefreshRequest(StrEnum):
    REFRESH_VIEW = "refresh_view"
    RECOMPARE = "recompare"


class ComparisonRefreshAction(StrEnum):
    LOAD_PERSISTED_SNAPSHOT = "load_persisted_snapshot"
    RECOMPUTE_COMPARISON = "recompute_comparison"


@dataclass(frozen=True, slots=True)
class ComparisonDependenciesFingerprint:
    youtube_playlist_version: str
    local_library_version: str
    ignored_terms_version: str
    matching_rules_version: str


def resolveComparisonRefreshAction(
    request: ComparisonRefreshRequest,
) -> ComparisonRefreshAction:
    if request is ComparisonRefreshRequest.REFRESH_VIEW:
        return ComparisonRefreshAction.LOAD_PERSISTED_SNAPSHOT
    return ComparisonRefreshAction.RECOMPUTE_COMPARISON


def shouldInvalidatePersistedFoundMatch(
    *,
    persisted_dependencies: ComparisonDependenciesFingerprint,
    current_dependencies: ComparisonDependenciesFingerprint,
    local_song_is_available: bool,
    force_recompute: bool = False,
) -> bool:
    if force_recompute:
        return True
    if not local_song_is_available:
        return True
    return persisted_dependencies != current_dependencies
