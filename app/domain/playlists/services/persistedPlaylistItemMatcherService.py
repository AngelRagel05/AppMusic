from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.playlists.services.matchDecisionSource import buildAutomaticMatchedBy
from app.domain.playlists.services.persistedComparisonModels import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
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
)
from app.shared.constants.comparison import ComparisonStatus


GENERIC_TITLE_TOKENS = frozenset(
    {
        "intro",
        "outro",
        "skit",
        "interlude",
        "interludio",
        "interludios",
        "intermedio",
        "prelude",
        "postlude",
    }
)


@dataclass(frozen=True, slots=True)
class PersistedPlaylistItemMatchResult:
    local_song: ComparableLocalSong | None
    comparison_status: ComparisonStatus
    score: float
    reason: str
    matched_by: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    local_song: ComparableLocalSong
    score: float
    score_breakdown: CandidateScoreBreakdown
    duration_distance: float
    evidence: CandidateMatchEvidence
    can_confirm_found: bool
    sort_key: tuple[int, float, float, int]


def matchPersistedPlaylistItemToLocalSongs(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    local_songs: Sequence[ComparableLocalSong],
) -> PersistedPlaylistItemMatchResult:
    if not local_songs:
        return PersistedPlaylistItemMatchResult(
            local_song=None,
            comparison_status=ComparisonStatus.MISSING,
            score=0.0,
            reason="No hay canciones locales candidatas validadas por titulo y artista.",
            matched_by=None,
        )

    valid_candidate_evaluations = [
        candidate_evaluation
        for local_song in local_songs
        if (
            candidate_evaluation := _evaluateValidatedCandidate(
                youtube_playlist_item,
                local_song,
            )
        )
        is not None
    ]
    if not valid_candidate_evaluations:
        return _buildMissingResult(
            reason="No hay canciones locales candidatas validadas por titulo y artista.",
        )

    valid_candidate_evaluations.sort(
        key=lambda evaluation: evaluation.sort_key,
        reverse=True,
    )
    best_evaluation = valid_candidate_evaluations[0]
    is_generic_title = _isGenericComparableTitle(youtube_playlist_item.comparable_title)

    if len(valid_candidate_evaluations) == 1:
        if best_evaluation.can_confirm_found:
            return _buildFoundResult(best_evaluation)
        return _buildMissingResult(
            reason=_buildDurationInsufficientReason(is_generic_title=is_generic_title),
        )

    second_best_evaluation = valid_candidate_evaluations[1]
    if not _hasClearWinningCandidate(best_evaluation, second_best_evaluation):
        return _buildPossibleMatchResult(
            best_evaluation,
            ambiguity_count=len(valid_candidate_evaluations),
        )

    if best_evaluation.can_confirm_found:
        return _buildFoundResult(best_evaluation)

    return _buildPossibleMatchResult(
        best_evaluation,
        ambiguity_count=len(valid_candidate_evaluations),
        reason=_buildDurationInsufficientReason(is_generic_title=is_generic_title),
    )


def _evaluateValidatedCandidate(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    local_song: ComparableLocalSong,
) -> CandidateEvaluation | None:
    title_evidence = _buildValidatedTitleEvidence(
        youtube_playlist_item.comparable_title,
        local_song.comparable_title,
    )
    artist_evidence = buildArtistMatchEvidence(
        youtube_playlist_item.comparable_artist,
        local_song.comparable_artist,
    )
    if title_evidence is TitleMatchEvidence.NONE:
        return None
    if artist_evidence is not ArtistMatchEvidence.STRONG:
        return None

    duration_evidence, duration_distance = buildDurationMatchEvidence(
        youtube_playlist_item.duration_seconds,
        local_song.duration_seconds,
    )
    score_breakdown = _buildScoreBreakdown(
        duration_evidence=duration_evidence,
        is_generic_title=_isGenericComparableTitle(youtube_playlist_item.comparable_title),
    )
    evidence = buildCandidateMatchEvidence(
        title_match=title_evidence,
        artist_match=artist_evidence,
        duration_match=duration_evidence,
    )
    can_confirm_found = _canConfirmFound(
        duration_evidence=duration_evidence,
        is_generic_title=_isGenericComparableTitle(youtube_playlist_item.comparable_title),
    )
    return CandidateEvaluation(
        local_song=local_song,
        score=score_breakdown.total_score,
        score_breakdown=score_breakdown,
        duration_distance=duration_distance,
        evidence=evidence,
        can_confirm_found=can_confirm_found,
        sort_key=(
            _durationEvidenceRank(duration_evidence),
            score_breakdown.total_score,
            -duration_distance,
            -(local_song.id or 0),
        ),
    )


def _buildValidatedTitleEvidence(
    left_title: str,
    right_title: str,
) -> TitleMatchEvidence:
    if left_title.strip() != right_title.strip():
        return TitleMatchEvidence.NONE
    return TitleMatchEvidence.EXACT


def _buildScoreBreakdown(
    *,
    duration_evidence: DurationMatchEvidence,
    is_generic_title: bool,
) -> CandidateScoreBreakdown:
    duration_score = {
        DurationMatchEvidence.STRONG: 60.0,
        DurationMatchEvidence.MEDIUM: 35.0,
        DurationMatchEvidence.UNKNOWN: 10.0,
        DurationMatchEvidence.WEAK: 0.0,
    }[duration_evidence]
    consistency_bonus = {
        DurationMatchEvidence.STRONG: 30.0 if is_generic_title else 20.0,
        DurationMatchEvidence.MEDIUM: 18.0 if is_generic_title else 12.0,
        DurationMatchEvidence.UNKNOWN: 0.0,
        DurationMatchEvidence.WEAK: 0.0,
    }[duration_evidence]
    return CandidateScoreBreakdown(
        title_score=0.0,
        artist_score=0.0,
        duration_score=duration_score,
        consistency_bonus=consistency_bonus,
    )


def _canConfirmFound(
    *,
    duration_evidence: DurationMatchEvidence,
    is_generic_title: bool,
) -> bool:
    if duration_evidence is DurationMatchEvidence.WEAK:
        return False
    if is_generic_title and duration_evidence is DurationMatchEvidence.UNKNOWN:
        return False
    return True


def _hasClearWinningCandidate(
    best_evaluation: CandidateEvaluation,
    second_best_evaluation: CandidateEvaluation,
) -> bool:
    if _durationEvidenceRank(best_evaluation.evidence.duration_match) > _durationEvidenceRank(
        second_best_evaluation.evidence.duration_match
    ):
        return True
    if best_evaluation.duration_distance + 1.0 < second_best_evaluation.duration_distance:
        return True
    return best_evaluation.score >= second_best_evaluation.score + 15.0


def _buildFoundResult(
    candidate_evaluation: CandidateEvaluation,
) -> PersistedPlaylistItemMatchResult:
    return PersistedPlaylistItemMatchResult(
        local_song=candidate_evaluation.local_song,
        comparison_status=ComparisonStatus.FOUND,
        score=candidate_evaluation.score,
        reason="Coincidencia confirmada por titulo y artista validos.",
        matched_by=buildAutomaticMatchedBy(
            status=ComparisonStatus.FOUND,
            evidence=candidate_evaluation.evidence,
        ),
    )


def _buildPossibleMatchResult(
    candidate_evaluation: CandidateEvaluation,
    *,
    ambiguity_count: int,
    reason: str | None = None,
) -> PersistedPlaylistItemMatchResult:
    evidence = buildCandidateMatchEvidence(
        title_match=candidate_evaluation.evidence.title_match,
        artist_match=candidate_evaluation.evidence.artist_match,
        duration_match=candidate_evaluation.evidence.duration_match,
        ambiguity_count=ambiguity_count,
    )
    return PersistedPlaylistItemMatchResult(
        local_song=candidate_evaluation.local_song,
        comparison_status=ComparisonStatus.POSSIBLE_MATCH,
        score=candidate_evaluation.score,
        reason=reason or "Varias candidatas del mismo titulo y artista.",
        matched_by=buildAutomaticMatchedBy(
            status=ComparisonStatus.POSSIBLE_MATCH,
            evidence=evidence,
        ),
    )


def _buildMissingResult(
    *,
    reason: str,
) -> PersistedPlaylistItemMatchResult:
    return PersistedPlaylistItemMatchResult(
        local_song=None,
        comparison_status=ComparisonStatus.MISSING,
        score=0.0,
        reason=reason,
        matched_by=None,
    )


def _buildDurationInsufficientReason(
    *,
    is_generic_title: bool,
) -> str:
    return "Duracion dudosa entre candidatas validas."


def _isGenericComparableTitle(title: str) -> bool:
    title_tokens = tuple(token for token in title.strip().split(" ") if token)
    if not title_tokens:
        return False
    return all(token in GENERIC_TITLE_TOKENS for token in title_tokens)


def _durationEvidenceRank(evidence: DurationMatchEvidence) -> int:
    return {
        DurationMatchEvidence.STRONG: 3,
        DurationMatchEvidence.MEDIUM: 2,
        DurationMatchEvidence.UNKNOWN: 1,
        DurationMatchEvidence.WEAK: 0,
    }[evidence]
