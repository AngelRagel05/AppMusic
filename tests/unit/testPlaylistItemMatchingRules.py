from __future__ import annotations

import pytest

from app.domain.playlists.services import (
    AmbiguityPenaltyThresholds,
    AUTO_AMBIGUOUS,
    AUTO_NO_COMPETITIVE_CANDIDATE,
    AUTO_TITLE_ARTIST_DURATION,
    ArtistMatchEvidence,
    CandidateMatchEvidence,
    CandidateScoreBreakdown,
    ConsistencyScoreWeights,
    DurationMatchEvidence,
    DurationMatchThresholds,
    TextMatchWeights,
    TitleMatchEvidence,
    buildAutomaticMatchedBy,
    calculateAmbiguityPenalty,
    buildMatchReason,
    buildArtistMatchEvidence,
    buildDurationMatchEvidence,
    buildTextMatchEvidence,
    classifyMatchStatus,
    normalizedSimilarityRatio,
    scoreDuration,
    scoreEvidenceConsistency,
    scoreNormalizedText,
    isAutomaticMatchedBy,
    isManualMatchedBy,
)
from app.shared.constants.comparison import ComparisonStatus


def test_score_normalized_text_returns_exact_score_for_exact_match() -> None:
    weights = TextMatchWeights(
        exact_score=60.0,
        contains_score=45.0,
        strong_overlap_score=35.0,
        medium_overlap_score=25.0,
    )

    assert scoreNormalizedText("song one", "song one", weights) == 60.0


def test_score_normalized_text_returns_contains_score_for_embedded_text() -> None:
    weights = TextMatchWeights(
        exact_score=60.0,
        contains_score=45.0,
        strong_overlap_score=35.0,
        medium_overlap_score=25.0,
    )

    assert scoreNormalizedText("artist one", "artist one feat guest", weights) == 45.0


def test_build_text_match_evidence_returns_exact_for_same_values() -> None:
    assert buildTextMatchEvidence("song one", "song one") is TitleMatchEvidence.EXACT


def test_build_artist_match_evidence_returns_strong_for_artist_with_collaborator_noise() -> None:
    assert (
        buildArtistMatchEvidence("artist one", "artist one feat guest")
        is ArtistMatchEvidence.STRONG
    )


def test_build_duration_match_evidence_uses_new_lte_1s_and_lte_3s_buckets() -> None:
    strong_evidence, strong_distance = buildDurationMatchEvidence(180.0, 180.8)
    medium_evidence, medium_distance = buildDurationMatchEvidence(180.0, 182.5)
    weak_evidence, weak_distance = buildDurationMatchEvidence(180.0, 185.0)

    assert strong_evidence.value == "lte_1s"
    assert strong_distance == pytest.approx(0.8)
    assert medium_evidence.value == "lte_3s"
    assert medium_distance == pytest.approx(2.5)
    assert weak_evidence.value == "gt_3s"
    assert weak_distance == pytest.approx(5.0)


def test_score_duration_returns_zero_without_textual_signal() -> None:
    score, distance = scoreDuration(
        180.0,
        181.0,
        has_textual_signal=False,
        thresholds=DurationMatchThresholds(),
    )

    assert score == 0.0
    assert distance == float("inf")


def test_score_duration_returns_weak_score_for_any_duration_over_3_seconds() -> None:
    score, distance = scoreDuration(
        180.0,
        195.0,
        has_textual_signal=True,
        thresholds=DurationMatchThresholds(),
    )

    assert score == 2.0
    assert distance == pytest.approx(15.0)


def test_score_evidence_consistency_adds_bonus_for_global_alignment() -> None:
    bonus = scoreEvidenceConsistency(
        CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=buildDurationMatchEvidence(180.0, 180.4)[0],
        ),
        ConsistencyScoreWeights(),
    )

    assert bonus == pytest.approx(20.0)


def test_calculate_ambiguity_penalty_scales_with_competitors() -> None:
    penalty = calculateAmbiguityPenalty(
        3,
        AmbiguityPenaltyThresholds(per_competitor_penalty=6.0),
    )

    assert penalty == 12.0


def test_classify_match_status_returns_found_for_exact_title_artist_and_good_duration() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=buildDurationMatchEvidence(180.0, 181.0)[0],
        )
    )

    assert status is ComparisonStatus.FOUND


def test_build_match_reason_returns_possible_match_reason_with_score_breakdown() -> None:
    reason = buildMatchReason(
        status=ComparisonStatus.POSSIBLE_MATCH,
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.NONE,
            duration_match=buildDurationMatchEvidence(180.0, 182.0)[0],
            ambiguity_count=2,
        ),
        score_breakdown=CandidateScoreBreakdown(
            title_score=60.0,
            artist_score=0.0,
            duration_score=6.0,
            consistency_bonus=5.0,
            ambiguity_penalty=6.0,
        ),
    )

    assert reason == "Ambiguedad entre dos candidatas plausibles."


def test_classify_match_status_returns_missing_for_contains_title_even_with_strong_artist() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.CONTAINS,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=buildDurationMatchEvidence(180.0, 180.8)[0],
        )
    )

    assert status is ComparisonStatus.MISSING


def test_classify_match_status_returns_found_for_near_exact_title_and_strong_artist() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.NEAR_EXACT,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=buildDurationMatchEvidence(180.0, 188.0)[0],
        )
    )

    assert status is ComparisonStatus.FOUND


def test_classify_match_status_returns_possible_for_exact_title_without_artist_and_duration_over_1s() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.NONE,
            duration_match=buildDurationMatchEvidence(180.0, 182.0)[0],
        )
    )

    assert status is ComparisonStatus.POSSIBLE_MATCH


def test_classify_match_status_returns_possible_for_real_ambiguity() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.NEAR_EXACT,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=buildDurationMatchEvidence(180.0, 180.6)[0],
            ambiguity_count=2,
        )
    )

    assert status is ComparisonStatus.POSSIBLE_MATCH


def test_classify_match_status_returns_missing_without_competitive_title_signal() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.WEAK,
            artist_match=ArtistMatchEvidence.NONE,
            duration_match=buildDurationMatchEvidence(180.0, 189.0)[0],
        )
    )

    assert status is ComparisonStatus.MISSING


def test_classify_match_status_returns_missing_for_exact_title_with_medium_artist() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.MEDIUM,
            duration_match=buildDurationMatchEvidence(180.0, 180.4)[0],
        )
    )

    assert status is ComparisonStatus.MISSING


def test_classify_match_status_returns_missing_for_exact_title_without_artist_and_duration_under_1s() -> None:
    status = classifyMatchStatus(
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.NONE,
            duration_match=buildDurationMatchEvidence(180.0, 180.6)[0],
        )
    )

    assert status is ComparisonStatus.MISSING


def test_build_match_reason_returns_specific_reason_for_exact_title_inconsistent_artist() -> None:
    reason = buildMatchReason(
        status=ComparisonStatus.POSSIBLE_MATCH,
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.NONE,
            duration_match=buildDurationMatchEvidence(180.0, 182.0)[0],
        ),
        score_breakdown=CandidateScoreBreakdown(
            title_score=60.0,
            artist_score=0.0,
            duration_score=6.0,
            consistency_bonus=0.0,
        ),
    )

    assert reason == "Titulo exacto pero artista inconsistente."


def test_build_automatic_matched_by_returns_found_source_code() -> None:
    matched_by = buildAutomaticMatchedBy(
        status=ComparisonStatus.FOUND,
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=DurationMatchEvidence.STRONG,
        ),
    )

    assert matched_by == AUTO_TITLE_ARTIST_DURATION


def test_build_automatic_matched_by_returns_ambiguity_source_code() -> None:
    matched_by = buildAutomaticMatchedBy(
        status=ComparisonStatus.POSSIBLE_MATCH,
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.EXACT,
            artist_match=ArtistMatchEvidence.STRONG,
            duration_match=DurationMatchEvidence.STRONG,
            ambiguity_count=2,
        ),
    )

    assert matched_by == AUTO_AMBIGUOUS


def test_build_automatic_matched_by_returns_non_competitive_source_code_for_missing() -> None:
    matched_by = buildAutomaticMatchedBy(
        status=ComparisonStatus.MISSING,
        evidence=CandidateMatchEvidence(
            title_match=TitleMatchEvidence.NONE,
            artist_match=ArtistMatchEvidence.NONE,
            duration_match=DurationMatchEvidence.WEAK,
        ),
    )

    assert matched_by == AUTO_NO_COMPETITIVE_CANDIDATE


def test_match_decision_source_helpers_identify_auto_and_manual_codes() -> None:
    assert isAutomaticMatchedBy(AUTO_TITLE_ARTIST_DURATION) is True
    assert isManualMatchedBy("manual:user_marked_missing") is True
    assert isAutomaticMatchedBy("manual:user_marked_missing") is False
    assert isManualMatchedBy("legacy free text") is False


def test_normalized_similarity_ratio_detects_near_equivalent_strings() -> None:
    assert normalizedSimilarityRatio("perdiendo la fe", "perdiendo fe") >= 0.78
