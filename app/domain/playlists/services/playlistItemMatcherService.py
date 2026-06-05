from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.library.entities.localSong import LocalSong
from app.domain.metadata.services import normalizeMusicComparisonMetadata
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.shared.constants.comparison import ComparisonStatus


FOUND_MINIMUM_SCORE = 85.0
POSSIBLE_MATCH_MINIMUM_SCORE = 55.0
FOUND_DURATION_TOLERANCE_SECONDS = 5.0
FOUND_MINIMUM_TITLE_SCORE = 45.0
FOUND_MINIMUM_ARTIST_SCORE = 10.0


@dataclass(frozen=True, slots=True)
class PlaylistItemMatchResult:
    local_song: LocalSong | None
    comparison_status: ComparisonStatus
    score: float
    reason: str


def matchYoutubePlaylistItemToLocalSongs(
    youtube_playlist_item: YoutubePlaylistItem,
    local_songs: Sequence[LocalSong],
) -> PlaylistItemMatchResult:
    best_result: PlaylistItemMatchResult | None = None
    best_sort_key: tuple[float, float, float, float, int] | None = None

    for local_song in local_songs:
        candidate_result, candidate_sort_key = _scoreCandidate(
            youtube_playlist_item,
            local_song,
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

    if best_result.score < POSSIBLE_MATCH_MINIMUM_SCORE:
        return PlaylistItemMatchResult(
            local_song=None,
            comparison_status=ComparisonStatus.MISSING,
            score=0.0,
            reason="No existe una candidata local con score minimo suficiente.",
        )

    return best_result


def _scoreCandidate(
    youtube_playlist_item: YoutubePlaylistItem,
    local_song: LocalSong,
) -> tuple[PlaylistItemMatchResult, tuple[float, float, float, float, int]]:
    normalized_local_song = normalizeMusicComparisonMetadata(
        title=local_song.title or local_song.file_name,
        artist=local_song.artist,
    )

    title_score = _scoreNormalizedText(
        youtube_playlist_item.normalized_title,
        normalized_local_song.normalized_title,
        exact_score=60.0,
        contains_score=45.0,
        strong_overlap_score=35.0,
        medium_overlap_score=25.0,
    )
    artist_score = _scoreNormalizedText(
        youtube_playlist_item.normalized_artist,
        normalized_local_song.normalized_artist,
        exact_score=30.0,
        contains_score=20.0,
        strong_overlap_score=15.0,
        medium_overlap_score=10.0,
    )
    duration_score, duration_distance = _scoreDuration(
        youtube_playlist_item.duration_seconds,
        local_song.duration_seconds,
        has_textual_signal=(title_score > 0.0 or artist_score > 0.0),
    )

    total_score = title_score + artist_score + duration_score
    status = _classifyMatchStatus(
        title_score=title_score,
        artist_score=artist_score,
        youtube_duration_seconds=youtube_playlist_item.duration_seconds,
        local_duration_seconds=local_song.duration_seconds,
        duration_distance=duration_distance,
        total_score=total_score,
    )
    reason = _buildReason(
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


def _scoreNormalizedText(
    left_value: str,
    right_value: str,
    *,
    exact_score: float,
    contains_score: float,
    strong_overlap_score: float,
    medium_overlap_score: float,
) -> float:
    left = left_value.strip()
    right = right_value.strip()
    if not left or not right:
        return 0.0
    if left == right:
        return exact_score
    if _containsEitherWay(left, right):
        return contains_score

    overlap_ratio = _tokenOverlapRatio(left, right)
    if overlap_ratio >= 0.75:
        return strong_overlap_score
    if overlap_ratio >= 0.5:
        return medium_overlap_score
    return 0.0


def _scoreDuration(
    youtube_duration_seconds: float | None,
    local_duration_seconds: float,
    *,
    has_textual_signal: bool,
) -> tuple[float, float]:
    if not has_textual_signal:
        return 0.0, float("inf")
    if youtube_duration_seconds is None or youtube_duration_seconds <= 0:
        return 0.0, float("inf")
    if local_duration_seconds <= 0:
        return 0.0, float("inf")

    distance = abs(youtube_duration_seconds - local_duration_seconds)
    if distance <= 3:
        return 10.0, distance
    if distance <= 5:
        return 6.0, distance
    if distance <= 8:
        return 3.0, distance
    return 0.0, distance


def _classifyMatchStatus(
    *,
    title_score: float,
    artist_score: float,
    youtube_duration_seconds: float | None,
    local_duration_seconds: float,
    duration_distance: float,
    total_score: float,
) -> ComparisonStatus:
    has_comparable_duration = (
        youtube_duration_seconds is not None
        and youtube_duration_seconds > 0
        and local_duration_seconds > 0
    )
    duration_is_strong = (not has_comparable_duration) or (
        duration_distance <= FOUND_DURATION_TOLERANCE_SECONDS
    )

    if (
        title_score >= FOUND_MINIMUM_TITLE_SCORE
        and artist_score >= FOUND_MINIMUM_ARTIST_SCORE
        and duration_is_strong
        and total_score >= FOUND_MINIMUM_SCORE
    ):
        return ComparisonStatus.FOUND
    if total_score >= POSSIBLE_MATCH_MINIMUM_SCORE:
        return ComparisonStatus.POSSIBLE_MATCH
    return ComparisonStatus.MISSING


def _buildReason(
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
