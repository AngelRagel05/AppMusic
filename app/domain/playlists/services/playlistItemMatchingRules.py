from __future__ import annotations

from dataclasses import dataclass

from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class TextMatchWeights:
    exact_score: float
    contains_score: float
    strong_overlap_score: float
    medium_overlap_score: float


@dataclass(frozen=True, slots=True)
class DurationMatchThresholds:
    strong_seconds: float = 3.0
    medium_seconds: float = 5.0
    weak_seconds: float = 8.0
    strong_score: float = 10.0
    medium_score: float = 6.0
    weak_score: float = 3.0


@dataclass(frozen=True, slots=True)
class MatchClassificationThresholds:
    found_minimum_score: float = 85.0
    possible_match_minimum_score: float = 55.0
    found_duration_tolerance_seconds: float = 5.0
    found_minimum_title_score: float = 45.0
    found_minimum_artist_score: float = 10.0


@dataclass(frozen=True, slots=True)
class PlaylistItemMatchingRuleset:
    title_weights: TextMatchWeights = TextMatchWeights(
        exact_score=60.0,
        contains_score=45.0,
        strong_overlap_score=35.0,
        medium_overlap_score=25.0,
    )
    artist_weights: TextMatchWeights = TextMatchWeights(
        exact_score=30.0,
        contains_score=20.0,
        strong_overlap_score=15.0,
        medium_overlap_score=10.0,
    )
    duration_thresholds: DurationMatchThresholds = DurationMatchThresholds()
    classification_thresholds: MatchClassificationThresholds = (
        MatchClassificationThresholds()
    )


DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET = PlaylistItemMatchingRuleset()


def scoreNormalizedText(
    left_value: str,
    right_value: str,
    weights: TextMatchWeights,
) -> float:
    left = left_value.strip()
    right = right_value.strip()
    if not left or not right:
        return 0.0
    if left == right:
        return weights.exact_score
    if containsEitherWay(left, right):
        return weights.contains_score

    overlap_ratio = tokenOverlapRatio(left, right)
    if overlap_ratio >= 0.75:
        return weights.strong_overlap_score
    if overlap_ratio >= 0.5:
        return weights.medium_overlap_score
    return 0.0


def scoreDuration(
    youtube_duration_seconds: float | None,
    local_duration_seconds: float,
    *,
    has_textual_signal: bool,
    thresholds: DurationMatchThresholds,
) -> tuple[float, float]:
    if not has_textual_signal:
        return 0.0, float("inf")
    if youtube_duration_seconds is None or youtube_duration_seconds <= 0:
        return 0.0, float("inf")
    if local_duration_seconds <= 0:
        return 0.0, float("inf")

    distance = abs(youtube_duration_seconds - local_duration_seconds)
    if distance <= thresholds.strong_seconds:
        return thresholds.strong_score, distance
    if distance <= thresholds.medium_seconds:
        return thresholds.medium_score, distance
    if distance <= thresholds.weak_seconds:
        return thresholds.weak_score, distance
    return 0.0, distance


def classifyMatchStatus(
    *,
    title_score: float,
    artist_score: float,
    youtube_duration_seconds: float | None,
    local_duration_seconds: float,
    duration_distance: float,
    total_score: float,
    thresholds: MatchClassificationThresholds,
) -> ComparisonStatus:
    has_comparable_duration = (
        youtube_duration_seconds is not None
        and youtube_duration_seconds > 0
        and local_duration_seconds > 0
    )
    duration_is_strong = (not has_comparable_duration) or (
        duration_distance <= thresholds.found_duration_tolerance_seconds
    )

    if (
        title_score >= thresholds.found_minimum_title_score
        and artist_score >= thresholds.found_minimum_artist_score
        and duration_is_strong
        and total_score >= thresholds.found_minimum_score
    ):
        return ComparisonStatus.FOUND
    if total_score >= thresholds.possible_match_minimum_score:
        return ComparisonStatus.POSSIBLE_MATCH
    return ComparisonStatus.MISSING


def buildMatchReason(
    *,
    status: ComparisonStatus,
    title_score: float,
    artist_score: float,
    duration_distance: float,
    total_score: float,
) -> str:
    if status is ComparisonStatus.FOUND:
        if duration_distance != float("inf"):
            return (
                "Coincidencia ponderada fuerte en titulo y artista normalizados; "
                f"duracion dentro de tolerancia ({duration_distance:.1f}s)."
            )
        return "Coincidencia ponderada fuerte en titulo y artista normalizados."
    if status is ComparisonStatus.POSSIBLE_MATCH:
        duration_note = ""
        if duration_distance != float("inf") and duration_distance <= 8:
            duration_note = f" y duracion cercana ({duration_distance:.1f}s)"
        return (
            "Coincidencia parcial detectada"
            f"{duration_note}. Score {total_score:.1f} "
            f"(titulo {title_score:.1f}, artista {artist_score:.1f})."
        )
    return "La candidata no alcanza score minimo de comparacion."


def containsEitherWay(left: str, right: str) -> bool:
    if len(left) < 3 or len(right) < 3:
        return False
    return left in right or right in left


def tokenOverlapRatio(left: str, right: str) -> float:
    left_tokens = {token for token in left.split(" ") if token}
    right_tokens = {token for token in right.split(" ") if token}
    if not left_tokens or not right_tokens:
        return 0.0
    intersection_size = len(left_tokens & right_tokens)
    denominator = max(len(left_tokens), len(right_tokens))
    return intersection_size / denominator
