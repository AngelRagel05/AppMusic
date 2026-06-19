from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
import re

from app.shared.constants.comparison import ComparisonStatus


class TitleMatchEvidence(str, Enum):
    EXACT = "exact"
    NEAR_EXACT = "near_exact"
    CONTAINS = "contains"
    WEAK = "weak"
    NONE = "none"


class ArtistMatchEvidence(str, Enum):
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"
    NONE = "none"


class DurationMatchEvidence(str, Enum):
    STRONG = "lte_1s"
    MEDIUM = "lte_3s"
    WEAK = "gt_3s"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TextMatchWeights:
    exact_score: float
    contains_score: float
    strong_overlap_score: float
    medium_overlap_score: float


@dataclass(frozen=True, slots=True)
class DurationMatchThresholds:
    strong_seconds: float = 1.0
    medium_seconds: float = 3.0
    strong_score: float = 10.0
    medium_score: float = 6.0
    weak_score: float = 2.0


@dataclass(frozen=True, slots=True)
class ConsistencyScoreWeights:
    title_artist_bonus: float = 8.0
    title_duration_bonus: float = 5.0
    global_consistency_bonus: float = 7.0


@dataclass(frozen=True, slots=True)
class AmbiguityPenaltyThresholds:
    close_score_margin: float = 5.0
    per_competitor_penalty: float = 6.0


@dataclass(frozen=True, slots=True)
class MatchClassificationThresholds:
    ambiguity_score_margin: float = 5.0


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
    consistency_weights: ConsistencyScoreWeights = ConsistencyScoreWeights()
    ambiguity_thresholds: AmbiguityPenaltyThresholds = AmbiguityPenaltyThresholds()
    classification_thresholds: MatchClassificationThresholds = (
        MatchClassificationThresholds()
    )


DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET = PlaylistItemMatchingRuleset()


@dataclass(frozen=True, slots=True)
class CandidateMatchEvidence:
    title_match: TitleMatchEvidence
    artist_match: ArtistMatchEvidence
    duration_match: DurationMatchEvidence
    ambiguity_count: int = 1


@dataclass(frozen=True, slots=True)
class CandidateScoreBreakdown:
    title_score: float
    artist_score: float
    duration_score: float
    consistency_bonus: float
    ambiguity_penalty: float = 0.0

    @property
    def base_score(self) -> float:
        return (
            self.title_score
            + self.artist_score
            + self.duration_score
            + self.consistency_bonus
        )

    @property
    def total_score(self) -> float:
        return self.base_score - self.ambiguity_penalty


def buildTextMatchEvidence(
    left_value: str,
    right_value: str,
) -> TitleMatchEvidence:
    left = left_value.strip()
    right = right_value.strip()
    if not left or not right:
        return TitleMatchEvidence.NONE
    if left == right:
        return TitleMatchEvidence.EXACT
    if containsEitherWay(left, right):
        return TitleMatchEvidence.CONTAINS

    overlap_ratio = tokenOverlapRatio(left, right)
    similarity_ratio = normalizedSimilarityRatio(left, right)
    if overlap_ratio >= 0.75 or similarity_ratio >= 0.9 or similarity_ratio >= 0.78:
        return TitleMatchEvidence.NEAR_EXACT
    if overlap_ratio >= 0.5 or similarity_ratio >= 0.64:
        return TitleMatchEvidence.WEAK
    return TitleMatchEvidence.NONE


def buildArtistMatchEvidence(
    left_value: str,
    right_value: str,
) -> ArtistMatchEvidence:
    if _normalizeCompactAlphanumericSpacing(left_value) == _normalizeCompactAlphanumericSpacing(
        right_value
    ):
        return ArtistMatchEvidence.STRONG

    title_like_evidence = buildTextMatchEvidence(left_value, right_value)
    overlap_ratio = tokenOverlapRatio(left_value, right_value)
    return {
        TitleMatchEvidence.EXACT: ArtistMatchEvidence.STRONG,
        TitleMatchEvidence.CONTAINS: ArtistMatchEvidence.STRONG,
        TitleMatchEvidence.NEAR_EXACT: (
            ArtistMatchEvidence.STRONG
            if overlap_ratio >= 0.75
            else ArtistMatchEvidence.MEDIUM
        ),
        TitleMatchEvidence.WEAK: ArtistMatchEvidence.WEAK,
        TitleMatchEvidence.NONE: ArtistMatchEvidence.NONE,
    }[title_like_evidence]


def buildDurationMatchEvidence(
    youtube_duration_seconds: float | None,
    local_duration_seconds: float,
) -> tuple[DurationMatchEvidence, float]:
    if (
        youtube_duration_seconds is None
        or youtube_duration_seconds <= 0
        or local_duration_seconds <= 0
    ):
        return DurationMatchEvidence.UNKNOWN, float("inf")

    distance = abs(youtube_duration_seconds - local_duration_seconds)
    if distance <= 1.0:
        return DurationMatchEvidence.STRONG, distance
    if distance <= 3.0:
        return DurationMatchEvidence.MEDIUM, distance
    return DurationMatchEvidence.WEAK, distance


def buildCandidateMatchEvidence(
    *,
    title_match: TitleMatchEvidence,
    artist_match: ArtistMatchEvidence,
    duration_match: DurationMatchEvidence,
    ambiguity_count: int = 1,
) -> CandidateMatchEvidence:
    return CandidateMatchEvidence(
        title_match=title_match,
        artist_match=artist_match,
        duration_match=duration_match,
        ambiguity_count=max(ambiguity_count, 1),
    )


def scoreNormalizedText(
    left_value: str,
    right_value: str,
    weights: TextMatchWeights,
) -> float:
    evidence = buildTextMatchEvidence(left_value, right_value)
    return {
        TitleMatchEvidence.EXACT: weights.exact_score,
        TitleMatchEvidence.CONTAINS: weights.contains_score,
        TitleMatchEvidence.NEAR_EXACT: weights.strong_overlap_score,
        TitleMatchEvidence.WEAK: weights.medium_overlap_score,
        TitleMatchEvidence.NONE: 0.0,
    }[evidence]


def scoreDuration(
    youtube_duration_seconds: float | None,
    local_duration_seconds: float,
    *,
    has_textual_signal: bool,
    thresholds: DurationMatchThresholds,
) -> tuple[float, float]:
    if not has_textual_signal:
        return 0.0, float("inf")
    duration_evidence, distance = buildDurationMatchEvidence(
        youtube_duration_seconds,
        local_duration_seconds,
    )
    if duration_evidence is DurationMatchEvidence.UNKNOWN:
        return 0.0, float("inf")
    if duration_evidence is DurationMatchEvidence.STRONG:
        return thresholds.strong_score, distance
    if duration_evidence is DurationMatchEvidence.MEDIUM:
        return thresholds.medium_score, distance
    if duration_evidence is DurationMatchEvidence.WEAK:
        return thresholds.weak_score, distance
    return 0.0, distance


def scoreEvidenceConsistency(
    evidence: CandidateMatchEvidence,
    weights: ConsistencyScoreWeights,
) -> float:
    bonus = 0.0

    if evidence.title_match is TitleMatchEvidence.EXACT and evidence.artist_match in (
        ArtistMatchEvidence.STRONG,
        ArtistMatchEvidence.MEDIUM,
    ):
        bonus += weights.title_artist_bonus
    elif (
        evidence.title_match is TitleMatchEvidence.NEAR_EXACT
        and evidence.artist_match is ArtistMatchEvidence.STRONG
    ):
        bonus += weights.title_artist_bonus * 0.75

    if evidence.title_match is TitleMatchEvidence.EXACT and evidence.duration_match in (
        DurationMatchEvidence.STRONG,
        DurationMatchEvidence.MEDIUM,
    ):
        bonus += weights.title_duration_bonus
    elif (
        evidence.title_match is TitleMatchEvidence.NEAR_EXACT
        and evidence.duration_match is DurationMatchEvidence.STRONG
    ):
        bonus += weights.title_duration_bonus * 0.8

    if _isFoundMatch(evidence):
        bonus += weights.global_consistency_bonus

    return bonus


def calculateAmbiguityPenalty(
    ambiguity_count: int,
    thresholds: AmbiguityPenaltyThresholds,
) -> float:
    competitive_neighbors = max(ambiguity_count - 1, 0)
    return competitive_neighbors * thresholds.per_competitor_penalty


def classifyMatchStatus(
    *,
    evidence: CandidateMatchEvidence,
) -> ComparisonStatus:
    if _hasRealAmbiguity(evidence):
        return ComparisonStatus.POSSIBLE_MATCH

    if _isFoundMatch(evidence):
        return ComparisonStatus.FOUND

    if _isPossibleMatch(evidence):
        return ComparisonStatus.POSSIBLE_MATCH

    return ComparisonStatus.MISSING


def buildMatchReason(
    *,
    status: ComparisonStatus,
    evidence: CandidateMatchEvidence,
    score_breakdown: CandidateScoreBreakdown,
) -> str:
    if status is ComparisonStatus.FOUND:
        return _buildFoundReason(evidence)
    if status is ComparisonStatus.POSSIBLE_MATCH:
        return _buildPossibleReason(evidence)
    return _buildMissingReason(evidence, score_breakdown)


def _buildFoundReason(evidence: CandidateMatchEvidence) -> str:
    if evidence.title_match is TitleMatchEvidence.EXACT:
        return "Coincidencia confirmada por titulo y artista validos."
    if evidence.title_match is TitleMatchEvidence.NEAR_EXACT:
        return "Titulo casi exacto con artista fuerte."
    return "Coincidencia validada por titulo y artista fuertes."


def _buildPossibleReason(evidence: CandidateMatchEvidence) -> str:
    if evidence.ambiguity_count > 1:
        return "Varias candidatas del mismo titulo y artista."
    return "Coincidencia valida pero no se puede confirmar de forma automatica."


def _buildMissingReason(
    evidence: CandidateMatchEvidence,
    score_breakdown: CandidateScoreBreakdown,
) -> str:
    if score_breakdown.base_score <= 0:
        return "No hay canciones locales candidatas para comparar."

    return "No hay candidata suficientemente competitiva."


def _isFoundMatch(evidence: CandidateMatchEvidence) -> bool:
    if _hasStrongTitleAndArtist(evidence):
        return True
    return _hasExactTitleStrongArtistAndReasonableDuration(evidence)


def _isPossibleMatch(evidence: CandidateMatchEvidence) -> bool:
    return _hasRealAmbiguity(evidence)


def _hasRealAmbiguity(evidence: CandidateMatchEvidence) -> bool:
    return evidence.ambiguity_count > 1


def _hasStrongTitleAndArtist(evidence: CandidateMatchEvidence) -> bool:
    return (
        evidence.title_match in (
            TitleMatchEvidence.EXACT,
            TitleMatchEvidence.NEAR_EXACT,
        )
        and evidence.artist_match is ArtistMatchEvidence.STRONG
    )


def _hasExactTitleStrongArtistAndReasonableDuration(
    evidence: CandidateMatchEvidence,
) -> bool:
    return (
        evidence.title_match is TitleMatchEvidence.EXACT
        and evidence.artist_match is ArtistMatchEvidence.STRONG
        and evidence.duration_match in (
            DurationMatchEvidence.STRONG,
            DurationMatchEvidence.MEDIUM,
            DurationMatchEvidence.UNKNOWN,
        )
    )


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


def normalizedSimilarityRatio(left: str, right: str) -> float:
    return SequenceMatcher(a=left, b=right).ratio()


def _normalizeCompactAlphanumericSpacing(value: str) -> str:
    normalized_value = re.sub(r"\s+", " ", value.strip().lower())
    return re.sub(r"(?<=[a-z])\s+(?=\d)|(?<=\d)\s+(?=[a-z])", "", normalized_value)
