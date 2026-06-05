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
