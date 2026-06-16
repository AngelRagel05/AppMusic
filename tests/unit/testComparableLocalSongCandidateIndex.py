from __future__ import annotations

from app.domain.playlists.services import (
    CandidateSelectionStage,
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
    buildCandidateSelectionBatches,
    buildComparableLocalSongCandidateIndex,
)


def test_comparable_local_song_candidate_index_returns_exact_subset_first() -> None:
    candidate_index = buildComparableLocalSongCandidateIndex(
        [
            ComparableLocalSong(
                id=1,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=2,
                title="song one",
                artist="artist two",
                duration_seconds=181.0,
            ),
            ComparableLocalSong(
                id=3,
                title="other song",
                artist="artist one",
                duration_seconds=182.0,
            ),
        ]
    )

    batches = buildCandidateSelectionBatches(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert batches[0].stage is CandidateSelectionStage.EXACT
    assert [song.id for song in batches[0].local_songs] == [1, 2]


def test_comparable_local_song_candidate_index_returns_very_similar_subset_second() -> None:
    candidate_index = buildComparableLocalSongCandidateIndex(
        [
            ComparableLocalSong(
                id=1,
                title="song onee",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=2,
                title="song ones",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=3,
                title="totally different",
                artist="artist one",
                duration_seconds=180.0,
            ),
        ]
    )

    batches = buildCandidateSelectionBatches(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert [batch.stage for batch in batches] == [
        CandidateSelectionStage.VERY_SIMILAR,
        CandidateSelectionStage.BROAD,
    ]
    assert [song.id for song in batches[0].local_songs] == [2, 1]


def test_comparable_local_song_candidate_index_excludes_reserved_songs_from_all_batches() -> None:
    candidate_index = buildComparableLocalSongCandidateIndex(
        [
            ComparableLocalSong(
                id=1,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=2,
                title="song onee",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=3,
                title="other song",
                artist="artist one",
                duration_seconds=180.0,
            ),
        ]
    )

    batches = buildCandidateSelectionBatches(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
        reserved_local_song_ids={1, 3},
    )

    assert [batch.stage for batch in batches] == [CandidateSelectionStage.VERY_SIMILAR]
    assert [song.id for song in batches[0].local_songs] == [2]
