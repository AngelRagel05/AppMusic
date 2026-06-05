from __future__ import annotations

from dataclasses import dataclass
import re

from app.domain.metadata.services.musicComparisonNormalizationService import (
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
)

_BRACKET_PATTERN = re.compile(r"(\([^)]*\)|\[[^\]]*\])")
_SEPARATOR_PATTERN = re.compile(r"\s*-\s*", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class NormalizedYoutubePlaylistItemMetadata:
    normalized_title: str
    normalized_artist: str


def normalizeYoutubePlaylistItemMetadata(
    raw_title: str,
    raw_channel_name: str,
) -> NormalizedYoutubePlaylistItemMetadata:
    cleaned_title = normalizeMusicComparisonText(_removeDecorativeBrackets(raw_title))
    cleaned_channel_name = normalizeMusicComparisonText(
        _removeDecorativeBrackets(raw_channel_name)
    )

    artist_from_title, title_from_title = _splitArtistAndTitle(cleaned_title)
    if artist_from_title and title_from_title:
        return NormalizedYoutubePlaylistItemMetadata(
            normalized_title=title_from_title,
            normalized_artist=artist_from_title,
        )

    normalized_metadata = normalizeMusicComparisonMetadata(cleaned_title, cleaned_channel_name)
    return NormalizedYoutubePlaylistItemMetadata(
        normalized_title=normalized_metadata.normalized_title,
        normalized_artist=normalized_metadata.normalized_artist,
    )


def _removeDecorativeBrackets(value: str) -> str:
    result = value
    for match in _BRACKET_PATTERN.findall(value):
        normalized_content = normalizeMusicComparisonText(match[1:-1])
        if normalized_content != match[1:-1].strip().lower():
            result = result.replace(match, " ")
    return result


def _splitArtistAndTitle(value: str) -> tuple[str | None, str | None]:
    parts = _SEPARATOR_PATTERN.split(value, maxsplit=1)
    if len(parts) != 2:
        return None, None

    artist = normalizeMusicComparisonText(parts[0])
    title = normalizeMusicComparisonText(parts[1])
    if not artist or not title:
        return None, None

    return artist, title
