from __future__ import annotations

import pytest

from app.domain.library.entities.localSong import LocalSong
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.services import matchYoutubePlaylistItemToLocalSongs
from app.shared.constants.comparison import ComparisonStatus


def test_match_youtube_playlist_item_to_local_songs_returns_found_for_clear_match() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=181.0,
    )
    local_song = LocalSong(
        id=4,
        file_name="song-one.mp3",
        title="Song One",
        artist="Artist One",
        duration_seconds=180.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score >= 95.0


def test_match_youtube_playlist_item_to_local_songs_returns_missing_without_viable_candidate() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=181.0,
    )
    local_song = LocalSong(
        id=4,
        file_name="totally-different.mp3",
        title="Totally Different",
        artist="Another Artist",
        duration_seconds=240.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.score == 0.0


def test_match_youtube_playlist_item_to_local_songs_returns_missing_for_title_similarity_without_artist_or_duration_support() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=181.0,
    )
    local_song = LocalSong(
        id=4,
        file_name="song-one-live.mp3",
        title="Song One Live",
        artist="Another Artist",
        duration_seconds=181.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.score == 0.0


def test_match_youtube_playlist_item_to_local_songs_returns_missing_for_contains_title_when_duration_is_over_3_seconds() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One Remix",
        raw_channel_name="Artist One",
        normalized_title="song one remix",
        normalized_artist="artist one",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=4,
        file_name="song-one.mp3",
        title="Song One",
        artist="Artist One Variation",
        duration_seconds=184.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.score == 0.0


def test_match_youtube_playlist_item_to_local_songs_returns_found_for_partial_featured_artist_with_strong_total_score() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=4,
        file_name="song-one.mp3",
        title="Song One",
        artist="Artist One feat Guest Singer",
        duration_seconds=181.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score >= 85.0


def test_match_youtube_playlist_item_to_local_songs_breaks_ties_using_title_and_artist_strength() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=180.0,
    )
    weaker_candidate = LocalSong(
        id=4,
        file_name="song-one-live.mp3",
        title="Song One Live",
        artist="Artist One Remix",
        duration_seconds=180.0,
    )
    stronger_candidate = LocalSong(
        id=9,
        file_name="song-one.mp3",
        title="Song One",
        artist="Artist One Guest",
        duration_seconds=180.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(
        youtube_item,
        [weaker_candidate, stronger_candidate],
    )

    assert result.local_song == stronger_candidate
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_youtube_playlist_item_to_local_songs_returns_possible_for_real_ambiguity() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=180.0,
    )
    first_candidate = LocalSong(
        id=4,
        file_name="song-one.mp3",
        title="Song One",
        artist="Artist One ft Guest A",
        duration_seconds=180.4,
    )
    second_candidate = LocalSong(
        id=9,
        file_name="song-one-alt.mp3",
        title="Song One",
        artist="Artist One ft Guest B",
        duration_seconds=180.5,
    )

    result = matchYoutubePlaylistItemToLocalSongs(
        youtube_item,
        [first_candidate, second_candidate],
    )

    assert result.local_song is not None
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH


def test_match_youtube_playlist_item_to_local_songs_resolves_close_top_candidates_by_duration() -> None:
    youtube_item = YoutubePlaylistItem(
        id=1,
        youtube_playlist_id=9,
        external_video_id="abc123",
        position=1,
        raw_title="Song One",
        raw_channel_name="Artist One",
        normalized_title="song one",
        normalized_artist="artist one",
        duration_seconds=180.0,
    )
    best_candidate = LocalSong(
        id=4,
        file_name="song-one.mp3",
        title="Song One",
        artist="Artist One ft Guest A",
        duration_seconds=180.1,
    )
    second_candidate = LocalSong(
        id=9,
        file_name="song-one-alt.mp3",
        title="Song One",
        artist="Artist One ft Guest B",
        duration_seconds=180.8,
    )

    result = matchYoutubePlaylistItemToLocalSongs(
        youtube_item,
        [best_candidate, second_candidate],
    )

    assert result.local_song == best_candidate
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_youtube_playlist_item_to_local_songs_does_not_mark_topic_noise_as_missing() -> None:
    youtube_item = YoutubePlaylistItem(
        id=3,
        youtube_playlist_id=9,
        external_video_id="xyz987",
        position=3,
        raw_title="Frio (Official Video)",
        raw_channel_name="Milo J Topic",
        normalized_title="frio",
        normalized_artist="milo j",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=10,
        file_name="frio.mp3",
        title="Frio",
        artist="Milo J",
        duration_seconds=181.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is not ComparisonStatus.MISSING
    assert result.score >= 55.0


def test_match_youtube_playlist_item_to_local_songs_returns_found_for_numbered_title_with_feature_noise() -> None:
    youtube_item = YoutubePlaylistItem(
        id=12,
        youtube_playlist_id=9,
        external_video_id="track010",
        position=10,
        raw_title="10. Space Hammu - I PROMISE ft. Raggio",
        raw_channel_name="Space Hammu",
        normalized_title="i promise",
        normalized_artist="space hammu",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=15,
        file_name="i-promise.mp3",
        title="I promise",
        artist="Space Hammu",
        duration_seconds=181.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score >= 75.0


def test_match_youtube_playlist_item_to_local_songs_recomputes_youtube_normalization_from_raw_fields() -> None:
    youtube_item = YoutubePlaylistItem(
        id=22,
        youtube_playlist_id=9,
        external_video_id="stale-normalized",
        position=4,
        raw_title="CRUZ CAFUNÉ - Practice ft. HOKE (Visualizer)",
        raw_channel_name="Cruz Cafuné",
        normalized_title="cruz cafune practice ft hoke visualizer",
        normalized_artist="cruz cafune practice ft hoke visualizer",
        duration_seconds=228.0,
    )
    local_song = LocalSong(
        id=31,
        file_name="practice.mp3",
        title="Practice",
        artist="Cruz Cafuné ft Hoke",
        duration_seconds=227.8,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score >= 75.0


@pytest.mark.parametrize(
    ("raw_title", "raw_channel_name", "local_title", "local_artist", "local_duration"),
    [
        (
            "Cruz Cafuné - Folelé ft. BOJ (Visualizer)",
            "Cruz Cafuné",
            "Folelé",
            "Cruz Cafuné",
            227.8,
        ),
        (
            "CRUZ CAFUNÉ - Practice ft. HOKE (Visualizer)",
            "Cruz Cafuné",
            "Practice",
            "Cruz Cafuné ft Hoke",
            227.8,
        ),
        (
            "CRUZ CAFUNÉ - G WAGON ft. LA PANTERA (Visualizer)",
            "Cruz Cafuné",
            "G Wagon",
            "Cruz Cafuné ft La Pantera",
            201.0,
        ),
        (
            "SFDK & Mama San - Éshate Pa Cá",
            "SFDK Oficial",
            "Éshate Pa Cá",
            "SFDK & Mama San",
            246.0,
        ),
        (
            "SFDK & Abbi Fernández - Donde Duele Más",
            "SFDK Oficial",
            "Donde Duele Más",
            "SFDK & Abbi Fernández",
            232.0,
        ),
    ],
)
def test_match_youtube_playlist_item_to_local_songs_finds_real_catalog_regressions(
    raw_title: str,
    raw_channel_name: str,
    local_title: str,
    local_artist: str,
    local_duration: float,
) -> None:
    youtube_item = YoutubePlaylistItem(
        id=40,
        youtube_playlist_id=9,
        external_video_id="real-case",
        position=1,
        raw_title=raw_title,
        raw_channel_name=raw_channel_name,
        normalized_title=raw_title.lower(),
        normalized_artist=raw_channel_name.lower(),
        duration_seconds=local_duration,
    )
    local_song = LocalSong(
        id=41,
        file_name="real-case.mp3",
        title=local_title,
        artist=local_artist,
        duration_seconds=local_duration,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_youtube_playlist_item_to_local_songs_returns_missing_for_platos_rotos_with_exact_title_and_inconsistent_artist() -> None:
    youtube_item = YoutubePlaylistItem(
        id=50,
        youtube_playlist_id=9,
        external_video_id="platos-rotos",
        position=3,
        raw_title="Platos Rotos",
        raw_channel_name="Natos y Waor",
        normalized_title="platos rotos",
        normalized_artist="natos y waor",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=51,
        file_name="platos-rotos.mp3",
        title="Platos Rotos",
        artist="Otro Artista",
        duration_seconds=180.4,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Titulo competitivo pero artista inconsistente."


def test_match_youtube_playlist_item_to_local_songs_returns_missing_for_exact_title_without_artist_and_duration_under_1s() -> None:
    youtube_item = YoutubePlaylistItem(
        id=60,
        youtube_playlist_id=9,
        external_video_id="exact-no-artist-strong-duration",
        position=1,
        raw_title="Cancion Exacta",
        raw_channel_name="Canal Ruido",
        normalized_title="cancion exacta",
        normalized_artist="canal ruido",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=61,
        file_name="cancion-exacta.mp3",
        title="Cancion Exacta",
        artist="",
        duration_seconds=180.6,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING


def test_match_youtube_playlist_item_to_local_songs_returns_possible_for_exact_title_without_artist_and_duration_over_1s() -> None:
    youtube_item = YoutubePlaylistItem(
        id=62,
        youtube_playlist_id=9,
        external_video_id="exact-no-artist-medium-duration",
        position=1,
        raw_title="Cancion Exacta",
        raw_channel_name="Canal Ruido",
        normalized_title="cancion exacta",
        normalized_artist="canal ruido",
        duration_seconds=180.0,
    )
    local_song = LocalSong(
        id=63,
        file_name="cancion-exacta.mp3",
        title="Cancion Exacta",
        artist="",
        duration_seconds=182.0,
    )

    result = matchYoutubePlaylistItemToLocalSongs(youtube_item, [local_song])

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert result.reason == "Titulo exacto pero artista inconsistente."
