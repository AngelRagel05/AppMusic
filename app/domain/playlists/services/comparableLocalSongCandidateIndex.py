from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
from typing import Iterable

from app.domain.playlists.services.persistedComparisonModels import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
)


class CandidateSelectionStage(str, Enum):
    EXACT = "exact"
    VERY_SIMILAR = "very_similar"
    BROAD = "broad"


@dataclass(frozen=True, slots=True)
class ComparableLocalSongCandidateIndex:
    local_song_by_id: dict[int, ComparableLocalSong]
    local_song_ids_by_title: dict[str, tuple[int, ...]]
    local_song_ids_by_artist: dict[str, tuple[int, ...]]
    local_song_ids_by_title_artist: dict[tuple[str, str], tuple[int, ...]]


@dataclass(frozen=True, slots=True)
class CandidateSelectionBatch:
    stage: CandidateSelectionStage
    local_songs: tuple[ComparableLocalSong, ...]


VERY_SIMILAR_TITLE_RATIO = 0.93


def buildComparableLocalSongCandidateIndex(
    local_songs: Iterable[ComparableLocalSong],
) -> ComparableLocalSongCandidateIndex:
    local_song_by_id: dict[int, ComparableLocalSong] = {}
    local_song_ids_by_title: dict[str, list[int]] = {}
    local_song_ids_by_artist: dict[str, list[int]] = {}
    local_song_ids_by_title_artist: dict[tuple[str, str], list[int]] = {}

    for local_song in local_songs:
        local_song_by_id[local_song.id] = local_song
        local_song_ids_by_title.setdefault(local_song.title, []).append(local_song.id)
        local_song_ids_by_artist.setdefault(local_song.artist, []).append(local_song.id)
        local_song_ids_by_title_artist.setdefault(
            (local_song.title, local_song.artist),
            [],
        ).append(local_song.id)

    return ComparableLocalSongCandidateIndex(
        local_song_by_id=local_song_by_id,
        local_song_ids_by_title={
            key: tuple(value) for key, value in local_song_ids_by_title.items()
        },
        local_song_ids_by_artist={
            key: tuple(value) for key, value in local_song_ids_by_artist.items()
        },
        local_song_ids_by_title_artist={
            key: tuple(value) for key, value in local_song_ids_by_title_artist.items()
        },
    )


def buildCandidateSelectionBatches(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    candidate_index: ComparableLocalSongCandidateIndex,
    *,
    reserved_local_song_ids: set[int] | None = None,
) -> tuple[CandidateSelectionBatch, ...]:
    reserved_ids = reserved_local_song_ids or set()
    yielded_ids: set[int] = set()
    batches: list[CandidateSelectionBatch] = []

    exact_ids = _collectExactCandidateIds(
        youtube_playlist_item,
        candidate_index,
        reserved_ids=reserved_ids,
        excluded_ids=yielded_ids,
    )
    if exact_ids:
        batches.append(
            CandidateSelectionBatch(
                stage=CandidateSelectionStage.EXACT,
                local_songs=_mapIdsToSongs(candidate_index, exact_ids),
            )
        )
        yielded_ids.update(exact_ids)

    very_similar_ids = _collectVerySimilarTitleCandidateIds(
        youtube_playlist_item,
        candidate_index,
        reserved_ids=reserved_ids,
        excluded_ids=yielded_ids,
    )
    if very_similar_ids:
        batches.append(
            CandidateSelectionBatch(
                stage=CandidateSelectionStage.VERY_SIMILAR,
                local_songs=_mapIdsToSongs(candidate_index, very_similar_ids),
            )
        )
        yielded_ids.update(very_similar_ids)

    broad_ids = _collectBroadCandidateIds(
        youtube_playlist_item,
        candidate_index,
        reserved_ids=reserved_ids,
        excluded_ids=yielded_ids,
    )
    if broad_ids:
        batches.append(
            CandidateSelectionBatch(
                stage=CandidateSelectionStage.BROAD,
                local_songs=_mapIdsToSongs(candidate_index, broad_ids),
            )
        )

    return tuple(batches)


def _collectExactCandidateIds(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    candidate_index: ComparableLocalSongCandidateIndex,
    *,
    reserved_ids: set[int],
    excluded_ids: set[int],
) -> tuple[int, ...]:
    ordered_ids: list[int] = []
    seen_ids: set[int] = set()
    for candidate_ids in (
        candidate_index.local_song_ids_by_title_artist.get(
            (
                youtube_playlist_item.normalized_title,
                youtube_playlist_item.normalized_artist,
            ),
            (),
        ),
        candidate_index.local_song_ids_by_title.get(
            youtube_playlist_item.normalized_title,
            (),
        ),
    ):
        for local_song_id in candidate_ids:
            if local_song_id in reserved_ids or local_song_id in excluded_ids:
                continue
            if local_song_id in seen_ids:
                continue
            ordered_ids.append(local_song_id)
            seen_ids.add(local_song_id)
    return tuple(ordered_ids)


def _collectVerySimilarTitleCandidateIds(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    candidate_index: ComparableLocalSongCandidateIndex,
    *,
    reserved_ids: set[int],
    excluded_ids: set[int],
) -> tuple[int, ...]:
    ranked_title_matches: list[tuple[float, str]] = []
    for local_title in candidate_index.local_song_ids_by_title.keys():
        if local_title == youtube_playlist_item.normalized_title:
            continue
        similarity_ratio = SequenceMatcher(
            a=youtube_playlist_item.normalized_title,
            b=local_title,
        ).ratio()
        if similarity_ratio < VERY_SIMILAR_TITLE_RATIO:
            continue
        ranked_title_matches.append((similarity_ratio, local_title))

    ranked_title_matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
    ordered_ids: list[int] = []
    seen_ids: set[int] = set()
    for _similarity_ratio, local_title in ranked_title_matches:
        for local_song_id in candidate_index.local_song_ids_by_title.get(local_title, ()):
            if local_song_id in reserved_ids or local_song_id in excluded_ids:
                continue
            if local_song_id in seen_ids:
                continue
            ordered_ids.append(local_song_id)
            seen_ids.add(local_song_id)
    return tuple(ordered_ids)


def _collectBroadCandidateIds(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    candidate_index: ComparableLocalSongCandidateIndex,
    *,
    reserved_ids: set[int],
    excluded_ids: set[int],
) -> tuple[int, ...]:
    ordered_ids: list[int] = []
    seen_ids: set[int] = set()

    for local_song_id in candidate_index.local_song_ids_by_artist.get(
        youtube_playlist_item.normalized_artist,
        (),
    ):
        if local_song_id in reserved_ids or local_song_id in excluded_ids:
            continue
        if local_song_id in seen_ids:
            continue
        ordered_ids.append(local_song_id)
        seen_ids.add(local_song_id)

    for local_song_id in sorted(candidate_index.local_song_by_id.keys()):
        if local_song_id in reserved_ids or local_song_id in excluded_ids:
            continue
        if local_song_id in seen_ids:
            continue
        ordered_ids.append(local_song_id)
        seen_ids.add(local_song_id)

    return tuple(ordered_ids)


def _mapIdsToSongs(
    candidate_index: ComparableLocalSongCandidateIndex,
    local_song_ids: tuple[int, ...],
) -> tuple[ComparableLocalSong, ...]:
    return tuple(candidate_index.local_song_by_id[local_song_id] for local_song_id in local_song_ids)
