from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.domain.playlists.services.persistedComparisonModels import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
)
from app.shared.constants.comparison import ComparisonStatus


@dataclass(frozen=True, slots=True)
class ComparableLocalSongSequentialIndex:
    local_song_by_id: dict[int, ComparableLocalSong]
    local_song_ids_by_title: dict[str, tuple[int, ...]]
    local_song_ids_by_title_artist: dict[tuple[str, str], tuple[int, ...]]


@dataclass(frozen=True, slots=True)
class SequentialCandidateSelectionResult:
    local_songs: tuple[ComparableLocalSong, ...]
    candidates_considered: int
    comparison_status: ComparisonStatus | None = None
    reason: str | None = None


def buildComparableLocalSongSequentialIndex(
    local_songs: Iterable[ComparableLocalSong],
) -> ComparableLocalSongSequentialIndex:
    local_song_by_id: dict[int, ComparableLocalSong] = {}
    local_song_ids_by_title: dict[str, list[int]] = {}
    local_song_ids_by_title_artist: dict[tuple[str, str], list[int]] = {}

    for local_song in local_songs:
        local_song_by_id[local_song.id] = local_song
        local_song_ids_by_title.setdefault(local_song.comparable_title, []).append(local_song.id)
        local_song_ids_by_title_artist.setdefault(
            (local_song.comparable_title, local_song.comparable_artist),
            [],
        ).append(local_song.id)

    return ComparableLocalSongSequentialIndex(
        local_song_by_id=local_song_by_id,
        local_song_ids_by_title={
            key: tuple(value) for key, value in local_song_ids_by_title.items()
        },
        local_song_ids_by_title_artist={
            key: tuple(value) for key, value in local_song_ids_by_title_artist.items()
        },
    )


def selectSequentialLocalSongCandidates(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    candidate_index: ComparableLocalSongSequentialIndex,
    *,
    reserved_local_song_ids: set[int] | None = None,
) -> SequentialCandidateSelectionResult:
    title_candidate_ids = candidate_index.local_song_ids_by_title.get(
        youtube_playlist_item.comparable_title,
        (),
    )
    if not title_candidate_ids:
        return SequentialCandidateSelectionResult(
            local_songs=(),
            candidates_considered=0,
            comparison_status=ComparisonStatus.MISSING,
            reason="No existe titulo en local.",
        )

    title_artist_candidate_ids = candidate_index.local_song_ids_by_title_artist.get(
        (
            youtube_playlist_item.comparable_title,
            youtube_playlist_item.comparable_artist,
        ),
        (),
    )
    if not title_artist_candidate_ids:
        return SequentialCandidateSelectionResult(
            local_songs=(),
            candidates_considered=0,
            comparison_status=ComparisonStatus.MISSING,
            reason="Existe titulo pero no artista.",
        )

    reserved_ids = reserved_local_song_ids or set()
    available_candidate_ids = tuple(
        local_song_id
        for local_song_id in title_artist_candidate_ids
        if local_song_id not in reserved_ids
    )
    if not available_candidate_ids:
        return SequentialCandidateSelectionResult(
            local_songs=(),
            candidates_considered=0,
            comparison_status=ComparisonStatus.MISSING,
            reason="La cancion local ya esta reservada por otro FOUND.",
        )

    local_songs = tuple(
        candidate_index.local_song_by_id[local_song_id]
        for local_song_id in available_candidate_ids
    )
    return SequentialCandidateSelectionResult(
        local_songs=local_songs,
        candidates_considered=len(local_songs),
    )
