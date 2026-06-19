from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.playlists.services.matchDecisionSource import buildAutomaticMatchedBy
from app.domain.playlists.services.persistedComparisonModels import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    AmbiguityPenaltyThresholds,
    ArtistMatchEvidence,
    CandidateMatchEvidence,
    CandidateScoreBreakdown,
    DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET,
    DurationMatchEvidence,
    PlaylistItemMatchingRuleset,
    TitleMatchEvidence,
    buildArtistMatchEvidence,
    buildCandidateMatchEvidence,
    buildDurationMatchEvidence,
    buildMatchReason,
    buildTextMatchEvidence,
    calculateAmbiguityPenalty,
    classifyMatchStatus,
    scoreDuration,
    scoreEvidenceConsistency,
    scoreNormalizedText,
)
from app.shared.constants.comparison import ComparisonStatus


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
    sort_key: tuple[float, float, float, float, float, float, int]


def matchPersistedPlaylistItemToLocalSongs(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    local_songs: Sequence[ComparableLocalSong],
    ruleset: PlaylistItemMatchingRuleset = DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET,
) -> PersistedPlaylistItemMatchResult:
    if not local_songs:
        return PersistedPlaylistItemMatchResult(
            local_song=None,
            comparison_status=ComparisonStatus.MISSING,
            score=0.0,
            reason="No hay canciones locales candidatas validadas por titulo y artista.",
            matched_by=None,
        )

    candidate_evaluations = [
        _scoreCandidate(youtube_playlist_item, local_song, ruleset)
        for local_song in local_songs
    ]
    candidate_evaluations.sort(
        key=lambda evaluation: evaluation.sort_key,
        reverse=True,
    )
    best_evaluation = _resolveTopCandidateAmbiguity(candidate_evaluations, ruleset)
    final_status = classifyMatchStatus(evidence=best_evaluation.evidence)
    final_reason = buildMatchReason(
        status=final_status,
        evidence=best_evaluation.evidence,
        score_breakdown=best_evaluation.score_breakdown,
    )
    final_matched_by = buildAutomaticMatchedBy(
        status=final_status,
        evidence=best_evaluation.evidence,
    )

    if final_status is ComparisonStatus.MISSING:
        return PersistedPlaylistItemMatchResult(
            local_song=None,
            comparison_status=ComparisonStatus.MISSING,
            score=0.0,
            reason=final_reason,
            matched_by=final_matched_by,
        )

    return PersistedPlaylistItemMatchResult(
        local_song=best_evaluation.local_song,
        comparison_status=final_status,
        score=best_evaluation.score,
        reason=final_reason,
        matched_by=final_matched_by,
    )


def _scoreCandidate(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    local_song: ComparableLocalSong,
    ruleset: PlaylistItemMatchingRuleset,
) -> CandidateEvaluation:
    title_evidence = buildTextMatchEvidence(
        youtube_playlist_item.comparable_title,
        local_song.comparable_title,
    )
    artist_evidence = buildArtistMatchEvidence(
        youtube_playlist_item.comparable_artist,
        local_song.comparable_artist,
    )
    title_score = scoreNormalizedText(
        youtube_playlist_item.comparable_title,
        local_song.comparable_title,
        ruleset.title_weights,
    )
    artist_score = scoreNormalizedText(
        youtube_playlist_item.comparable_artist,
        local_song.comparable_artist,
        ruleset.artist_weights,
    )
    duration_evidence, duration_distance = buildDurationMatchEvidence(
        youtube_playlist_item.duration_seconds,
        local_song.duration_seconds,
    )
    duration_score, duration_distance = scoreDuration(
        youtube_playlist_item.duration_seconds,
        local_song.duration_seconds,
        has_textual_signal=(title_score > 0.0 or artist_score > 0.0),
        thresholds=ruleset.duration_thresholds,
    )
    evidence = buildCandidateMatchEvidence(
        title_match=title_evidence,
        artist_match=artist_evidence,
        duration_match=duration_evidence,
    )
    score_breakdown = CandidateScoreBreakdown(
        title_score=title_score,
        artist_score=artist_score,
        duration_score=duration_score,
        consistency_bonus=scoreEvidenceConsistency(
            evidence,
            ruleset.consistency_weights,
        ),
    )
    return CandidateEvaluation(
        local_song=local_song,
        score=score_breakdown.total_score,
        score_breakdown=score_breakdown,
        duration_distance=duration_distance,
        evidence=evidence,
        sort_key=_buildRankingSortKey(
            title_match=title_evidence,
            artist_match=artist_evidence,
            duration_match=duration_evidence,
            score_breakdown=score_breakdown,
            duration_distance=duration_distance,
            local_song_id=local_song.id,
        ),
    )


def _resolveTopCandidateAmbiguity(
    candidate_evaluations: Sequence[CandidateEvaluation],
    ruleset: PlaylistItemMatchingRuleset,
) -> CandidateEvaluation:
    best_evaluation = candidate_evaluations[0]
    if len(candidate_evaluations) == 1:
        return best_evaluation

    second_best_evaluation = candidate_evaluations[1]
    if not _isPlausibleTopChallenger(
        best_evaluation,
        second_best_evaluation,
        ruleset.ambiguity_thresholds,
    ):
        return best_evaluation

    if _canSafelyResolveAgainstSecondBest(best_evaluation, second_best_evaluation):
        return best_evaluation

    ambiguity_penalty = calculateAmbiguityPenalty(
        2,
        ruleset.ambiguity_thresholds,
    )
    return _withResolvedAmbiguityContext(
        best_evaluation,
        ambiguity_count=2,
        ambiguity_penalty=ambiguity_penalty,
    )


def _isPlausibleTopChallenger(
    best_evaluation: CandidateEvaluation,
    second_best_evaluation: CandidateEvaluation,
    ambiguity_thresholds: AmbiguityPenaltyThresholds,
) -> bool:
    if second_best_evaluation.evidence.title_match is TitleMatchEvidence.NONE:
        return False
    return (
        second_best_evaluation.score_breakdown.base_score
        >= best_evaluation.score_breakdown.base_score
        - ambiguity_thresholds.close_score_margin
    )


def _canSafelyResolveAgainstSecondBest(
    best_evaluation: CandidateEvaluation,
    second_best_evaluation: CandidateEvaluation,
) -> bool:
    title_gap = _titleEvidenceRank(best_evaluation.evidence.title_match) - _titleEvidenceRank(
        second_best_evaluation.evidence.title_match
    )
    if title_gap > 0:
        return True

    artist_gap = _artistEvidenceRank(
        best_evaluation.evidence.artist_match
    ) - _artistEvidenceRank(second_best_evaluation.evidence.artist_match)
    if title_gap == 0 and artist_gap > 0:
        return True

    duration_gap = _durationEvidenceRank(
        best_evaluation.evidence.duration_match
    ) - _durationEvidenceRank(second_best_evaluation.evidence.duration_match)
    if title_gap == 0 and artist_gap == 0 and duration_gap > 0:
        return True

    if title_gap == 0 and artist_gap == 0 and duration_gap == 0:
        return best_evaluation.duration_distance + 0.5 < second_best_evaluation.duration_distance

    return False


def _withResolvedAmbiguityContext(
    candidate_evaluation: CandidateEvaluation,
    *,
    ambiguity_count: int,
    ambiguity_penalty: float,
) -> CandidateEvaluation:
    contextualized_evidence = buildCandidateMatchEvidence(
        title_match=candidate_evaluation.evidence.title_match,
        artist_match=candidate_evaluation.evidence.artist_match,
        duration_match=candidate_evaluation.evidence.duration_match,
        ambiguity_count=ambiguity_count,
    )
    contextualized_breakdown = CandidateScoreBreakdown(
        title_score=candidate_evaluation.score_breakdown.title_score,
        artist_score=candidate_evaluation.score_breakdown.artist_score,
        duration_score=candidate_evaluation.score_breakdown.duration_score,
        consistency_bonus=candidate_evaluation.score_breakdown.consistency_bonus,
        ambiguity_penalty=ambiguity_penalty,
    )
    return CandidateEvaluation(
        local_song=candidate_evaluation.local_song,
        score=contextualized_breakdown.total_score,
        score_breakdown=contextualized_breakdown,
        duration_distance=candidate_evaluation.duration_distance,
        evidence=contextualized_evidence,
        sort_key=_buildRankingSortKey(
            title_match=contextualized_evidence.title_match,
            artist_match=contextualized_evidence.artist_match,
            duration_match=contextualized_evidence.duration_match,
            score_breakdown=contextualized_breakdown,
            duration_distance=candidate_evaluation.duration_distance,
            local_song_id=candidate_evaluation.local_song.id,
        ),
    )


def _buildRankingSortKey(
    *,
    title_match: TitleMatchEvidence,
    artist_match: ArtistMatchEvidence,
    duration_match: DurationMatchEvidence,
    score_breakdown: CandidateScoreBreakdown,
    duration_distance: float,
    local_song_id: int | None,
) -> tuple[float, float, float, float, float, float, int]:
    return (
        _titleEvidenceRank(title_match),
        _artistEvidenceRank(artist_match),
        _durationEvidenceRank(duration_match),
        score_breakdown.base_score,
        -score_breakdown.ambiguity_penalty,
        -duration_distance,
        -(local_song_id or 0),
    )


def _titleEvidenceRank(evidence: TitleMatchEvidence) -> int:
    return {
        TitleMatchEvidence.EXACT: 4,
        TitleMatchEvidence.NEAR_EXACT: 3,
        TitleMatchEvidence.CONTAINS: 2,
        TitleMatchEvidence.WEAK: 1,
        TitleMatchEvidence.NONE: 0,
    }[evidence]


def _artistEvidenceRank(evidence: ArtistMatchEvidence) -> int:
    return {
        ArtistMatchEvidence.STRONG: 3,
        ArtistMatchEvidence.MEDIUM: 2,
        ArtistMatchEvidence.WEAK: 1,
        ArtistMatchEvidence.NONE: 0,
    }[evidence]


def _durationEvidenceRank(evidence: DurationMatchEvidence) -> int:
    return {
        DurationMatchEvidence.STRONG: 3,
        DurationMatchEvidence.MEDIUM: 2,
        DurationMatchEvidence.UNKNOWN: 1,
        DurationMatchEvidence.WEAK: 0,
    }[evidence]
