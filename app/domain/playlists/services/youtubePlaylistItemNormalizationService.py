from __future__ import annotations

from dataclasses import dataclass
import re


_DECORATIVE_TERMS = (
    "official video",
    "official audio",
    "lyrics",
    "hd",
    "4k",
    "remastered",
)
_BRACKET_PATTERN = re.compile(r"(\([^)]*\)|\[[^\]]*\])")
_SEPARATOR_PATTERN = re.compile(r"\s*-\s*", re.IGNORECASE)
_WHITESPACE_PATTERN = re.compile(r"\s+")
_LEADING_TRAILING_SEPARATORS_PATTERN = re.compile(r"^[\s\-–—:]+|[\s\-–—:]+$")


@dataclass(frozen=True, slots=True)
class NormalizedYoutubePlaylistItemMetadata:
    normalized_title: str
    normalized_artist: str


def normalizeYoutubePlaylistItemMetadata(
    raw_title: str,
    raw_channel_name: str,
) -> NormalizedYoutubePlaylistItemMetadata:
    cleaned_title = _normalizeText(_removeDecorativeBrackets(raw_title))
    cleaned_channel_name = _normalizeText(_removeDecorativeBrackets(raw_channel_name))

    artist_from_title, title_from_title = _splitArtistAndTitle(cleaned_title)
    if artist_from_title and title_from_title:
        return NormalizedYoutubePlaylistItemMetadata(
            normalized_title=title_from_title,
            normalized_artist=artist_from_title,
        )

    return NormalizedYoutubePlaylistItemMetadata(
        normalized_title=cleaned_title,
        normalized_artist=cleaned_channel_name,
    )


def _removeDecorativeBrackets(value: str) -> str:
    result = value
    for match in _BRACKET_PATTERN.findall(value):
        normalized_content = _normalizeText(match[1:-1])
        if any(term in normalized_content for term in _DECORATIVE_TERMS):
            result = result.replace(match, " ")
    return _removeDecorativeTerms(result)


def _removeDecorativeTerms(value: str) -> str:
    result = value
    for term in _DECORATIVE_TERMS:
        result = re.sub(re.escape(term), " ", result, flags=re.IGNORECASE)
    return result


def _splitArtistAndTitle(value: str) -> tuple[str | None, str | None]:
    parts = _SEPARATOR_PATTERN.split(value, maxsplit=1)
    if len(parts) != 2:
        return None, None

    artist = _normalizeText(parts[0])
    title = _normalizeText(parts[1])
    if not artist or not title:
        return None, None

    return artist, title


def _normalizeText(value: str) -> str:
    normalized_value = value.strip().lower()
    normalized_value = _LEADING_TRAILING_SEPARATORS_PATTERN.sub("", normalized_value)
    normalized_value = _WHITESPACE_PATTERN.sub(" ", normalized_value)
    return normalized_value.strip()
