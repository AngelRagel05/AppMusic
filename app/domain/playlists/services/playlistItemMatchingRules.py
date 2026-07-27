from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum


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
    if _containsEitherWay(left, right):
        return TitleMatchEvidence.CONTAINS

    overlap_ratio = _tokenOverlapRatio(left, right)
    similarity_ratio = _normalizedSimilarityRatio(left, right)
    if overlap_ratio >= 0.75 or similarity_ratio >= 0.78:
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
    overlap_ratio = _tokenOverlapRatio(left_value, right_value)
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


def _containsEitherWay(left: str, right: str) -> bool:
    if len(left) < 3 or len(right) < 3:
        return False
    return left in right or right in left


def _tokenOverlapRatio(left: str, right: str) -> float:
    left_tokens = {token for token in left.split(" ") if token}
    right_tokens = {token for token in right.split(" ") if token}
    if not left_tokens or not right_tokens:
        return 0.0
    intersection_size = len(left_tokens & right_tokens)
    denominator = max(len(left_tokens), len(right_tokens))
    return intersection_size / denominator


def _normalizedSimilarityRatio(left: str, right: str) -> float:
    return SequenceMatcher(a=left, b=right).ratio()


def _normalizeCompactAlphanumericSpacing(value: str) -> str:
    normalized_value = re.sub(r"\s+", " ", value.strip().lower())
    return re.sub(r"(?<=[a-z])\s+(?=\d)|(?<=\d)\s+(?=[a-z])", "", normalized_value)
