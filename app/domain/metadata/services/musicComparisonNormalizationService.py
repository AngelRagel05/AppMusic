from __future__ import annotations

from dataclasses import dataclass
import re


_DECORATIVE_TERMS = (
    "official",
    "video",
    "lyrics",
    "audio",
    "hd",
    "4k",
    "remastered",
)
_DECORATIVE_TERM_PATTERN = re.compile(
    rf"\b(?:{'|'.join(re.escape(term) for term in _DECORATIVE_TERMS)})\b",
    re.IGNORECASE,
)
_SEPARATOR_NORMALIZATION_PATTERN = re.compile(r"[_–—:]+")
_BRACKET_CHARACTER_PATTERN = re.compile(r"[\[\]\(\)\{\}]")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_LEADING_TRAILING_SEPARATORS_PATTERN = re.compile(r"^[\s\-–—:]+|[\s\-–—:]+$")


@dataclass(frozen=True, slots=True)
class NormalizedMusicComparisonMetadata:
    normalized_title: str
    normalized_artist: str


def normalizeMusicComparisonText(value: str) -> str:
    normalized_value = value.strip().lower()
    normalized_value = _SEPARATOR_NORMALIZATION_PATTERN.sub(" ", normalized_value)
    normalized_value = _BRACKET_CHARACTER_PATTERN.sub(" ", normalized_value)
    normalized_value = _DECORATIVE_TERM_PATTERN.sub(" ", normalized_value)
    normalized_value = _LEADING_TRAILING_SEPARATORS_PATTERN.sub("", normalized_value)
    normalized_value = _WHITESPACE_PATTERN.sub(" ", normalized_value)
    return normalized_value.strip()


def normalizeMusicComparisonMetadata(
    title: str,
    artist: str,
) -> NormalizedMusicComparisonMetadata:
    return NormalizedMusicComparisonMetadata(
        normalized_title=normalizeMusicComparisonText(title),
        normalized_artist=normalizeMusicComparisonText(artist),
    )
