from __future__ import annotations

from app.domain.playlists.services import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
    matchPersistedPlaylistItemToLocalSongs,
)
from app.shared.constants.comparison import ComparisonStatus


def test_match_persisted_playlist_item_to_local_songs_returns_found_for_single_validated_candidate() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=181.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 4
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score > 0.0
    assert result.reason == "Coincidencia confirmada por titulo y artista validos."


def test_match_persisted_playlist_item_to_local_songs_returns_missing_without_validated_candidates() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=181.0,
        ),
        [],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.score == 0.0
    assert result.reason == "Existe titulo pero no artista principal valido."


def test_match_persisted_playlist_item_to_local_songs_resolves_same_title_and_artist_by_duration() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=50,
            normalized_title="intro",
            normalized_artist_full="sfdk",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=51,
                title="intro",
                artist="sfdk",
                duration_seconds=180.1,
            ),
            ComparableLocalSong(
                id=52,
                title="intro",
                artist="sfdk",
                duration_seconds=183.8,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 51
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_persisted_playlist_item_to_local_songs_returns_possible_for_same_title_and_artist_ambiguity() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist_full="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one",
                duration_seconds=180.4,
            ),
            ComparableLocalSong(
                id=9,
                title="song one",
                artist="artist one",
                duration_seconds=180.5,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert result.reason == "Varias candidatas del mismo titulo y artista valido."


def test_match_persisted_playlist_item_to_local_songs_returns_found_for_nadal015_case() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=18,
            normalized_title="memories i",
            normalized_artist_full="nadal015",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=19,
                title="memories i",
                artist="nadal015",
                duration_seconds=175.848,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 19
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_persisted_playlist_item_to_local_songs_returns_found_when_local_artist_has_collaborators() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=60,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=61,
                title="beast mode",
                artist="Cruz Cafune feat West Dubai",
                normalized_title="beast mode",
                normalized_artist_full="cruz cafune west dubai",
                normalized_artist_primary="cruz cafune",
                normalized_artist_collaborators=("west dubai",),
                duration_seconds=176.2,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 61
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_persisted_playlist_item_to_local_songs_returns_possible_when_duplicates_share_same_primary_artist() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=62,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=63,
                title="beast mode",
                artist="Cruz Cafune feat West Dubai",
                normalized_title="beast mode",
                normalized_artist_full="cruz cafune west dubai",
                normalized_artist_primary="cruz cafune",
                normalized_artist_collaborators=("west dubai",),
                duration_seconds=176.2,
            ),
            ComparableLocalSong(
                id=64,
                title="beast mode",
                artist="Cruz Cafune feat Maikel Delacalle",
                normalized_title="beast mode",
                normalized_artist_full="cruz cafune maikel delacalle",
                normalized_artist_primary="cruz cafune",
                normalized_artist_collaborators=("maikel delacalle",),
                duration_seconds=176.3,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert result.reason == "Varias candidatas del mismo titulo y artista valido."


def test_match_persisted_playlist_item_to_local_songs_never_returns_found_without_valid_artist() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=22,
            normalized_title="intro",
            normalized_artist_full="sfdk",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=33,
                title="intro",
                artist="otro artista",
                duration_seconds=176.0,
            ),
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Existe titulo pero no artista principal valido."


def test_match_persisted_playlist_item_to_local_songs_rejects_weak_artist_containment() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=23,
            normalized_title="beast mode",
            normalized_artist_full="cruz cafune",
            normalized_artist_primary="cruz cafune",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=35,
                title="beast mode",
                artist="West Dubai feat Cruz Cafune",
                normalized_title="beast mode",
                normalized_artist_full="west dubai cruz cafune",
                normalized_artist_primary="west dubai",
                normalized_artist_collaborators=("cruz cafune",),
                duration_seconds=176.0,
            ),
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Existe titulo pero no artista principal valido."


def test_match_persisted_playlist_item_to_local_songs_returns_missing_when_only_title_matches() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=24,
            normalized_title="platos rotos",
            normalized_artist_full="sfdk",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=34,
                title="platos rotos",
                artist="otro artista",
                duration_seconds=176.0,
            ),
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Existe titulo pero no artista principal valido."


def test_match_persisted_playlist_item_to_local_songs_requires_duration_for_generic_title_found() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=44,
            normalized_title="intro",
            normalized_artist_full="sfdk",
            duration_seconds=None,
        ),
        [
            ComparableLocalSong(
                id=55,
                title="intro",
                artist="sfdk",
                duration_seconds=180.0,
            ),
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Duracion dudosa entre candidatas validas."


def test_match_persisted_playlist_item_to_local_songs_does_not_return_found_for_generic_title_with_weak_duration() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=46,
            normalized_title="intro",
            normalized_artist_full="sfdk",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=57,
                title="intro",
                artist="sfdk",
                duration_seconds=186.0,
            ),
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Duracion dudosa entre candidatas validas."
