from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.library.entities.localSong import LocalSong
from app.domain.metadata.services import normalizeMusicComparisonMetadata
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.services.playlistItemMatchingRules import (
    DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET,
    PlaylistItemMatchingRuleset,
    buildMatchReason,
    classifyMatchStatus,
    scoreDuration,
    scoreNormalizedText,
)
from app.domain.playlists.services.youtubePlaylistItemNormalizationService import (
    normalizeYoutubePlaylistItemMetadata,
)
from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class PlaylistItemMatchResult:
    local_song: LocalSong | None
    comparison_status: ComparisonStatus
    score: float
    reason: str


def matchYoutubePlaylistItemToLocalSongs(
    youtube_playlist_item: YoutubePlaylistItem,
    local_songs: Sequence[LocalSong],
    ruleset: PlaylistItemMatchingRuleset = DEFAULT_PLAYLIST_ITEM_MATCHING_RULESET,
) -> PlaylistItemMatchResult:
    comparable_youtube_playlist_item = _buildComparableYoutubePlaylistItem(
        youtube_playlist_item
    )
    best_result: PlaylistItemMatchResult | None = None
    best_sort_key: tuple[float, float, float, float, int] | None = None

    for local_song in local_songs:
        candidate_result, candidate_sort_key = _scoreCandidate(
            comparable_youtube_playlist_item,
            local_song,
            ruleset,
        )
        if best_sort_key is None or candidate_sort_key > best_sort_key:
            best_result = candidate_result
            best_sort_key = candidate_sort_key

    if best_result is None:
        return PlaylistItemMatchResult(
            local_song=None,
            comparison_status=ComparisonStatus.MISSING,
            score=0.0,
            reason="No hay canciones locales candidatas para comparar.",
        )

    if (
        best_result.score
        < ruleset.classification_thresholds.possible_match_minimum_score
    ):
        return PlaylistItemMatchResult(
            local_song=None,
            comparison_status=ComparisonStatus.MISSING,
            score=0.0,
            reason="No existe una candidata local con score minimo suficiente.",
        )

    return best_result


def _buildComparableYoutubePlaylistItem(
    youtube_playlist_item: YoutubePlaylistItem,
) -> YoutubePlaylistItem:
    raw_title = youtube_playlist_item.raw_title or youtube_playlist_item.normalized_title
    raw_channel_name = (
        youtube_playlist_item.raw_channel_name or youtube_playlist_item.normalized_artist
    )
    normalized_metadata = normalizeYoutubePlaylistItemMetadata(
        raw_title,
        raw_channel_name,
    )
    return YoutubePlaylistItem(
        id=youtube_playlist_item.id,
        youtube_playlist_id=youtube_playlist_item.youtube_playlist_id,
        external_video_id=youtube_playlist_item.external_video_id,
        position=youtube_playlist_item.position,
        raw_title=youtube_playlist_item.raw_title,
        raw_channel_name=youtube_playlist_item.raw_channel_name,
        normalized_title=normalized_metadata.normalized_title,
        normalized_artist=normalized_metadata.normalized_artist,
        duration_seconds=youtube_playlist_item.duration_seconds,
        published_at=youtube_playlist_item.published_at,
        created_at=youtube_playlist_item.created_at,
        updated_at=youtube_playlist_item.updated_at,
    )


def _scoreCandidate(
    youtube_playlist_item: YoutubePlaylistItem,
    local_song: LocalSong,
    ruleset: PlaylistItemMatchingRuleset,
) -> tuple[PlaylistItemMatchResult, tuple[float, float, float, float, int]]:
    normalized_local_song = normalizeMusicComparisonMetadata(
        title=local_song.title or local_song.file_name,
        artist=local_song.artist,
    )

    title_score = scoreNormalizedText(
        youtube_playlist_item.normalized_title,
        normalized_local_song.normalized_title,
        ruleset.title_weights,
    )
    artist_score = scoreNormalizedText(
        youtube_playlist_item.normalized_artist,
        normalized_local_song.normalized_artist,
        ruleset.artist_weights,
    )
    duration_score, duration_distance = scoreDuration(
        youtube_playlist_item.duration_seconds,
        local_song.duration_seconds,
        has_textual_signal=(title_score > 0.0 or artist_score > 0.0),
        thresholds=ruleset.duration_thresholds,
    )

    total_score = title_score + artist_score + duration_score
    status = classifyMatchStatus(
        title_score=title_score,
        artist_score=artist_score,
        youtube_duration_seconds=youtube_playlist_item.duration_seconds,
        local_duration_seconds=local_song.duration_seconds,
        duration_distance=duration_distance,
        total_score=total_score,
        thresholds=ruleset.classification_thresholds,
    )
    reason = buildMatchReason(
        status=status,
        title_score=title_score,
        artist_score=artist_score,
        duration_distance=duration_distance,
        total_score=total_score,
    )
    result = PlaylistItemMatchResult(
        local_song=local_song,
        comparison_status=status,
        score=total_score,
        reason=reason,
    )
    sort_key = (
        total_score,
        title_score,
        artist_score,
        -duration_distance,
        -(local_song.id or 0),
    )
    return result, sort_key
