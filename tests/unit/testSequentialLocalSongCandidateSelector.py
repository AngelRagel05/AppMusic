from __future__ import annotations

from app.domain.playlists.services import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
    buildComparableLocalSongSequentialIndex,
    selectSequentialLocalSongCandidates,
)
from app.shared.constants.comparison import ComparisonStatus


def test_sequential_local_song_candidate_selector_returns_title_and_artist_subset() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
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

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert selection.comparison_status is None
    assert selection.reason is None
    assert selection.candidates_considered == 1
    assert [song.id for song in selection.local_songs] == [1]


def test_sequential_local_song_candidate_index_groups_candidates_only_by_title() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
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
        ]
    )

    assert candidate_index.local_song_ids_by_title["song one"] == (1, 2)


def test_sequential_local_song_candidate_selector_uses_normalized_title_and_artist() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="Song One (Live at Home)",
                artist="Artist One feat Guest",
                normalized_title="song one",
                normalized_artist_full="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=2,
                title="Song One",
                artist="Another Artist",
                normalized_title="song one",
                normalized_artist_full="another artist",
                duration_seconds=181.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert selection.comparison_status is None
    assert [song.id for song in selection.local_songs] == [1]


def test_sequential_local_song_candidate_selector_returns_missing_without_title_match() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=7,
                title="another song",
                artist="artist one",
                duration_seconds=180.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert selection.local_songs == ()
    assert selection.candidates_considered == 0
    assert selection.comparison_status is ComparisonStatus.MISSING
    assert selection.reason == "No existe titulo en local."


def test_sequential_local_song_candidate_selector_returns_missing_when_title_exists_without_artist() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="song one",
                artist="another artist",
                duration_seconds=180.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert selection.local_songs == ()
    assert selection.candidates_considered == 0
    assert selection.comparison_status is ComparisonStatus.MISSING
    assert selection.reason == "Existe titulo pero no artista principal valido."


def test_sequential_local_song_candidate_selector_accepts_local_collaborators_when_primary_artist_matches() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="beast mode",
                artist="Cruz Cafune feat West Dubai",
                normalized_title="beast mode",
                normalized_artist_full="cruz cafune west dubai",
                normalized_artist_primary="cruz cafune",
                normalized_artist_collaborators=("west dubai",),
                duration_seconds=180.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert selection.comparison_status is None
    assert [song.id for song in selection.local_songs] == [1]


def test_sequential_local_song_candidate_selector_returns_multiple_candidates_when_primary_artist_matches_more_than_once() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="beast mode",
                artist="Cruz Cafune feat West Dubai",
                normalized_title="beast mode",
                normalized_artist_full="cruz cafune west dubai",
                normalized_artist_primary="cruz cafune",
                normalized_artist_collaborators=("west dubai",),
                duration_seconds=176.0,
            ),
            ComparableLocalSong(
                id=2,
                title="beast mode",
                artist="Cruz Cafune feat Maikel Delacalle",
                normalized_title="beast mode",
                normalized_artist_full="cruz cafune maikel delacalle",
                normalized_artist_primary="cruz cafune",
                normalized_artist_collaborators=("maikel delacalle",),
                duration_seconds=176.2,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=176.0,
        ),
        candidate_index,
    )

    assert selection.comparison_status is None
    assert selection.candidates_considered == 2
    assert [song.id for song in selection.local_songs] == [1, 2]


def test_sequential_local_song_candidate_selector_discards_medium_artist_matches() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="beast mode",
                artist="West Dubai feat Cruz Cafune",
                normalized_title="beast mode",
                normalized_artist_full="west dubai cruz cafune",
                normalized_artist_primary="west dubai",
                normalized_artist_collaborators=("cruz cafune",),
                duration_seconds=180.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=180.0,
        ),
        candidate_index,
    )

    assert selection.local_songs == ()
    assert selection.comparison_status is ComparisonStatus.MISSING
    assert selection.reason == "Existe titulo pero no artista principal valido."


def test_sequential_local_song_candidate_selector_returns_missing_when_title_exists_with_only_incorrect_full_artist_matches() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="beast mode",
                artist="West Dubai feat Cruz Cafune",
                normalized_title="beast mode",
                normalized_artist_full="west dubai cruz cafune",
                normalized_artist_primary="west dubai",
                normalized_artist_collaborators=("cruz cafune",),
                duration_seconds=176.0,
            ),
            ComparableLocalSong(
                id=2,
                title="beast mode",
                artist="Otro Artista",
                normalized_title="beast mode",
                normalized_artist_full="otro artista",
                normalized_artist_primary="otro artista",
                duration_seconds=176.3,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=176.0,
        ),
        candidate_index,
    )

    assert selection.local_songs == ()
    assert selection.candidates_considered == 0
    assert selection.comparison_status is ComparisonStatus.MISSING
    assert selection.reason == "Existe titulo pero no artista principal valido."


def test_sequential_local_song_candidate_selector_excludes_reserved_found_songs() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
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
                artist="artist one",
                duration_seconds=181.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
        reserved_local_song_ids={1},
    )

    assert selection.comparison_status is None
    assert selection.candidates_considered == 1
    assert [song.id for song in selection.local_songs] == [2]


def test_sequential_local_song_candidate_selector_returns_missing_when_all_artist_matches_are_reserved() -> None:
    candidate_index = buildComparableLocalSongSequentialIndex(
        [
            ComparableLocalSong(
                id=1,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            ),
        ]
    )

    selection = selectSequentialLocalSongCandidates(
        ComparableYoutubePlaylistItem(
            id=10,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        candidate_index,
        reserved_local_song_ids={1},
    )

    assert selection.local_songs == ()
    assert selection.candidates_considered == 0
    assert selection.comparison_status is ComparisonStatus.MISSING
    assert selection.reason == "La cancion local ya esta reservada por otro FOUND."
