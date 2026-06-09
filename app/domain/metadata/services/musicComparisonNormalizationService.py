from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


_DECORATIVE_TERMS = (
    "official video",
    "video oficial",
    "videoclip oficial",
    "official audio",
    "official",
    "video",
    "visualizer",
    "videoclip",
    "lyrics",
    "lyric",
    "letra",
    "audio",
    "prod",
    "produced",
    "producido",
    "topic",
    "hd",
    "4k",
    "remastered",
)
_DECORATIVE_TERM_PATTERN = re.compile(
    "|".join(re.escape(term) for term in _DECORATIVE_TERMS),
    re.IGNORECASE,
)
_SEPARATOR_NORMALIZATION_PATTERN = re.compile(r"[_–—:\-|/\\]+")
_BRACKET_CHARACTER_PATTERN = re.compile(r"[\[\]\(\)\{\}]")
_BRACKETED_CONTENT_PATTERN = re.compile(r"(\([^)]*\)|\[[^\]]*\]|\{[^}]*\})")
_FEATURE_PATTERN = re.compile(r"\b(featuring|feat\.?|ft\.?)\b", re.IGNORECASE)
_TRAILING_COLLABORATION_PATTERN = re.compile(
    r"\s+\b(feat|featuring|ft|con)\b\s+.*$",
    re.IGNORECASE,
)
_LEADING_TRACK_NUMBER_PATTERN = re.compile(r"^\s*\d{1,3}[\s\.\-\)_]+")
_SYMBOL_PATTERN = re.compile(r"[^a-z0-9\s-]")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_LEADING_TRAILING_SEPARATORS_PATTERN = re.compile(r"^[\s\-–—:]+|[\s\-–—:]+$")


@dataclass(frozen=True, slots=True)
class NormalizedMusicComparisonMetadata:
    normalized_title: str
    normalized_artist: str


def normalizeMusicComparisonText(value: str) -> str:
    normalized_value = _stripAccents(value.strip().lower())
    normalized_value = _removeDecorativeBracketedContent(normalized_value)
    normalized_value = _FEATURE_PATTERN.sub(" feat ", normalized_value)
    normalized_value = _SEPARATOR_NORMALIZATION_PATTERN.sub(" ", normalized_value)
    normalized_value = _DECORATIVE_TERM_PATTERN.sub(" ", normalized_value)
    normalized_value = _BRACKET_CHARACTER_PATTERN.sub(" ", normalized_value)
    normalized_value = _SYMBOL_PATTERN.sub(" ", normalized_value)
    normalized_value = _LEADING_TRAILING_SEPARATORS_PATTERN.sub("", normalized_value)
    normalized_value = _WHITESPACE_PATTERN.sub(" ", normalized_value)
    return normalized_value.strip()


def normalizeMusicComparisonMetadata(
    title: str,
    artist: str,
) -> NormalizedMusicComparisonMetadata:
    return NormalizedMusicComparisonMetadata(
        normalized_title=normalizeMusicComparisonTitle(title),
        normalized_artist=normalizeMusicComparisonArtist(artist),
    )


def normalizeMusicComparisonTitle(value: str) -> str:
    normalized_title = normalizeMusicComparisonText(value)
    normalized_title = _LEADING_TRACK_NUMBER_PATTERN.sub("", normalized_title)
    normalized_title = _TRAILING_COLLABORATION_PATTERN.sub("", normalized_title)
    normalized_title = _WHITESPACE_PATTERN.sub(" ", normalized_title)
    return normalized_title.strip()


def normalizeMusicComparisonArtist(value: str) -> str:
    normalized_artist = normalizeMusicComparisonText(value)
    normalized_artist = _LEADING_TRACK_NUMBER_PATTERN.sub("", normalized_artist)
    normalized_artist = _WHITESPACE_PATTERN.sub(" ", normalized_artist)
    return normalized_artist.strip()


def _stripAccents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _removeDecorativeBracketedContent(value: str) -> str:
    result = value
    for match in _BRACKETED_CONTENT_PATTERN.findall(value):
        bracket_content = match[1:-1].strip()
        if not bracket_content:
            result = result.replace(match, " ")
            continue
        normalized_content = _stripAccents(bracket_content.lower())
        if any(term in normalized_content for term in _DECORATIVE_TERMS):
            result = result.replace(match, " ")
    return result
