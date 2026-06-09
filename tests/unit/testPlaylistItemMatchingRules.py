from __future__ import annotations

from app.domain.playlists.services import (
    DurationMatchThresholds,
    MatchClassificationThresholds,
    TextMatchWeights,
    buildMatchReason,
    classifyMatchStatus,
    normalizedSimilarityRatio,
    scoreDuration,
    scoreNormalizedText,
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


def test_score_duration_returns_zero_without_textual_signal() -> None:
    score, distance = scoreDuration(
        180.0,
        181.0,
        has_textual_signal=False,
        thresholds=DurationMatchThresholds(),
    )

    assert score == 0.0
    assert distance == float("inf")


def test_classify_match_status_returns_found_with_weighted_thresholds() -> None:
    status = classifyMatchStatus(
        title_score=60.0,
        artist_score=20.0,
        youtube_duration_seconds=180.0,
        local_duration_seconds=181.0,
        duration_distance=1.0,
        total_score=90.0,
        thresholds=MatchClassificationThresholds(),
    )

    assert status is ComparisonStatus.FOUND


def test_build_match_reason_returns_possible_match_reason_with_score_breakdown() -> None:
    reason = buildMatchReason(
        status=ComparisonStatus.POSSIBLE_MATCH,
        title_score=45.0,
        artist_score=10.0,
        duration_distance=3.0,
        total_score=58.0,
    )

    assert "Score 58.0" in reason
    assert "titulo 45.0" in reason
    assert "artista 10.0" in reason


def test_classify_match_status_rescues_strong_title_and_partial_artist_matches() -> None:
    status = classifyMatchStatus(
        title_score=60.0,
        artist_score=20.0,
        youtube_duration_seconds=180.0,
        local_duration_seconds=196.0,
        duration_distance=16.0,
        total_score=80.0,
        thresholds=MatchClassificationThresholds(),
    )

    assert status is ComparisonStatus.FOUND


def test_classify_match_status_returns_found_with_lower_total_threshold_when_text_is_strong() -> None:
    status = classifyMatchStatus(
        title_score=45.0,
        artist_score=20.0,
        youtube_duration_seconds=180.0,
        local_duration_seconds=181.0,
        duration_distance=1.0,
        total_score=75.0,
        thresholds=MatchClassificationThresholds(),
    )

    assert status is ComparisonStatus.FOUND


def test_normalized_similarity_ratio_detects_near_equivalent_strings() -> None:
    assert normalizedSimilarityRatio("perdiendo la fe", "perdiendo fe") >= 0.78
