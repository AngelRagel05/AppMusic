from __future__ import annotations

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


def test_match_youtube_playlist_item_to_local_songs_returns_possible_match_for_title_similarity() -> None:
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

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert 55.0 <= result.score < 85.0


def test_match_youtube_playlist_item_to_local_songs_returns_possible_match_for_near_duration() -> None:
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

    assert result.local_song == local_song
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert result.score >= 55.0


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
