from __future__ import annotations

from dataclasses import dataclass
import re

from app.domain.metadata.services.musicComparisonNormalizationService import (
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
    normalizeMusicComparisonText,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    normalizedSimilarityRatio,
)

_BRACKET_PATTERN = re.compile(r"(\([^)]*\)|\[[^\]]*\])")
_SEPARATOR_PATTERN = re.compile(r"\s*(?:-{1,3}|[–—|·~]+|/{1,3})\s*", re.IGNORECASE)
_TRACK_INDEX_PATTERN = re.compile(r"^\d{1,3}[a-z]?$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class NormalizedYoutubePlaylistItemMetadata:
    normalized_title: str
    normalized_artist: str


def normalizeYoutubePlaylistItemMetadata(
    raw_title: str,
    raw_channel_name: str,
) -> NormalizedYoutubePlaylistItemMetadata:
    cleaned_raw_title = _removeDecorativeBrackets(raw_title)
    cleaned_title = normalizeMusicComparisonTitle(cleaned_raw_title)
    cleaned_channel_name = normalizeMusicComparisonText(
        _removeDecorativeBrackets(raw_channel_name)
    )

    artist_from_title, title_from_title = _splitArtistAndTitle(
        cleaned_raw_title,
        raw_channel_name,
    )
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


def _splitArtistAndTitle(
    value: str,
    raw_channel_name: str,
) -> tuple[str | None, str | None]:
    raw_parts = [part.strip() for part in _SEPARATOR_PATTERN.split(value) if part.strip()]
    if len(raw_parts) < 2:
        return None, None

    normalized_channel = normalizeMusicComparisonArtist(raw_channel_name)
    if len(raw_parts) >= 3 and _looksLikeTrackIndex(raw_parts[0]):
        title = normalizeMusicComparisonTitle(" ".join(raw_parts[1:-1]))
        artist = normalizeMusicComparisonArtist(raw_parts[-1])
        if artist and title:
            return artist, title

    if len(raw_parts) == 2:
        first_artist = normalizeMusicComparisonArtist(raw_parts[0])
        second_artist = normalizeMusicComparisonArtist(raw_parts[1])
        first_title = normalizeMusicComparisonTitle(raw_parts[0])
        second_title = normalizeMusicComparisonTitle(raw_parts[1])

        if _channelMatchesPart(normalized_channel, first_artist):
            return first_artist or None, second_title or None
        if _channelMatchesPart(normalized_channel, second_artist):
            return first_title or None, second_artist or None

        return first_artist or None, second_title or None

    first_artist = normalizeMusicComparisonArtist(raw_parts[0])
    trailing_artist = normalizeMusicComparisonArtist(" ".join(raw_parts[1:]))
    joined_title = normalizeMusicComparisonTitle(" ".join(raw_parts[1:]))
    if _channelMatchesPart(normalized_channel, first_artist):
        return first_artist or None, joined_title or None

    if _channelMatchesPart(normalized_channel, trailing_artist):
        title = normalizeMusicComparisonTitle(raw_parts[0])
        artist = trailing_artist
        if artist and title:
            return artist, title

    title = normalizeMusicComparisonTitle(raw_parts[0])
    artist = trailing_artist
    if artist and title:
        return artist, title
    return None, None


def _looksLikeTrackIndex(value: str) -> bool:
    normalized_value = normalizeMusicComparisonText(value)
    return bool(normalized_value and _TRACK_INDEX_PATTERN.fullmatch(normalized_value))


def _channelMatchesPart(normalized_channel: str, normalized_part: str) -> bool:
    if not normalized_channel or not normalized_part:
        return False
    if normalized_channel == normalized_part:
        return True
    if normalized_channel in normalized_part or normalized_part in normalized_channel:
        return True
    return normalizedSimilarityRatio(normalized_channel, normalized_part) >= 0.82
