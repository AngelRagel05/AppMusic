from __future__ import annotations

from dataclasses import dataclass
import re

from app.domain.metadata.services.musicComparisonNormalizationService import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
    normalizeMusicComparisonTitle,
    splitMusicComparisonSegments,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    TitleMatchEvidence,
    buildTextMatchEvidence,
)


@dataclass(frozen=True, slots=True)
class NormalizedYoutubePlaylistItemMetadata:
    normalized_title: str
    normalized_artist: str


@dataclass(frozen=True, slots=True)
class _SplitCandidate:
    normalized_artist: str
    normalized_title: str
    channel_rank: int
    title_token_count: int
    artist_token_count: int


_TRACK_INDEX_PATTERN = re.compile(r"^\d{1,3}[a-z]?$", re.IGNORECASE)


def normalizeYoutubePlaylistItemMetadata(
    raw_title: str,
    raw_channel_name: str,
) -> NormalizedYoutubePlaylistItemMetadata:
    artist_from_title, title_from_title = _splitArtistAndTitle(
        raw_title,
        raw_channel_name,
    )
    if artist_from_title and title_from_title:
        return NormalizedYoutubePlaylistItemMetadata(
            normalized_title=title_from_title,
            normalized_artist=artist_from_title,
        )

    normalized_metadata = normalizeMusicComparisonMetadata(
        title=raw_title,
        artist=raw_channel_name,
    )
    return NormalizedYoutubePlaylistItemMetadata(
        normalized_title=normalized_metadata.normalized_title,
        normalized_artist=normalized_metadata.normalized_artist,
    )


def _splitArtistAndTitle(
    value: str,
    raw_channel_name: str,
) -> tuple[str | None, str | None]:
    raw_parts = list(splitMusicComparisonSegments(value))
    if len(raw_parts) < 2:
        return None, None

    if _looksLikeTrackIndex(raw_parts[0]):
        raw_parts = raw_parts[1:]
    if len(raw_parts) < 2:
        return None, None

    normalized_channel = normalizeMusicComparisonArtist(raw_channel_name)
    split_candidates = _buildSplitCandidates(raw_parts, normalized_channel)
    if split_candidates:
        best_candidate = max(
            split_candidates,
            key=lambda candidate: (
                candidate.channel_rank,
                candidate.title_token_count,
                -candidate.artist_token_count,
            ),
        )
        if best_candidate.channel_rank >= 2:
            return (
                best_candidate.normalized_artist or None,
                best_candidate.normalized_title or None,
            )

    default_artist = normalizeMusicComparisonArtist(raw_parts[0])
    default_title = normalizeMusicComparisonTitle(" ".join(raw_parts[1:]))
    if default_artist and default_title:
        return default_artist, default_title
    return None, None


def _buildSplitCandidates(
    raw_parts: list[str],
    normalized_channel: str,
) -> list[_SplitCandidate]:
    split_candidates: list[_SplitCandidate] = []
    for split_index in range(1, len(raw_parts)):
        left_raw_value = " ".join(raw_parts[:split_index])
        right_raw_value = " ".join(raw_parts[split_index:])
        left_artist = normalizeMusicComparisonArtist(left_raw_value)
        right_artist = normalizeMusicComparisonArtist(right_raw_value)
        left_title = normalizeMusicComparisonTitle(left_raw_value)
        right_title = normalizeMusicComparisonTitle(right_raw_value)

        if left_artist and right_title:
            split_candidates.append(
                _buildSplitCandidate(
                    normalized_artist=left_artist,
                    normalized_title=right_title,
                    normalized_channel=normalized_channel,
                )
            )
        if right_artist and left_title:
            split_candidates.append(
                _buildSplitCandidate(
                    normalized_artist=right_artist,
                    normalized_title=left_title,
                    normalized_channel=normalized_channel,
                )
            )
    return split_candidates


def _buildSplitCandidate(
    *,
    normalized_artist: str,
    normalized_title: str,
    normalized_channel: str,
) -> _SplitCandidate:
    return _SplitCandidate(
        normalized_artist=normalized_artist,
        normalized_title=normalized_title,
        channel_rank=_rankChannelMatch(normalized_channel, normalized_artist),
        title_token_count=len([token for token in normalized_title.split(" ") if token]),
        artist_token_count=len([token for token in normalized_artist.split(" ") if token]),
    )


def _looksLikeTrackIndex(value: str) -> bool:
    normalized_value = normalizeMusicComparisonText(value)
    return bool(normalized_value and _TRACK_INDEX_PATTERN.fullmatch(normalized_value))


def _rankChannelMatch(normalized_channel: str, normalized_artist: str) -> int:
    if not normalized_channel or not normalized_artist:
        return 0

    evidence = buildTextMatchEvidence(normalized_channel, normalized_artist)
    return {
        TitleMatchEvidence.EXACT: 3,
        TitleMatchEvidence.NEAR_EXACT: 2,
        TitleMatchEvidence.CONTAINS: 1,
        TitleMatchEvidence.WEAK: 0,
        TitleMatchEvidence.NONE: 0,
    }[evidence]
