from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonSearch import (
    filterComparisonItemsByQuery,
    filterLocalSongsByQuery,
)
from app.shared.constants.comparison import ComparisonStatus


def test_filter_local_songs_by_query_matches_title_artist_album_and_file_name() -> None:
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=7,
            file_path=r"C:\Music\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            album="Album A",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.0,
        ),
        LocalSongDto(
            id=2,
            local_folder_id=7,
            file_path=r"C:\Music\jazz-night.mp3",
            file_name="jazz-night.mp3",
            is_available=True,
            title="Jazz Night",
            artist="Blue Trio",
            album="Late Set",
            release_year=2020,
            track_number_album=2,
            duration_seconds=210.0,
        ),
    ]

    assert filterLocalSongsByQuery(local_songs, "artist one") == [local_songs[0]]
    assert filterLocalSongsByQuery(local_songs, "late set") == [local_songs[1]]
    assert filterLocalSongsByQuery(local_songs, "jazz-night.mp3") == [local_songs[1]]


def test_filter_comparison_items_by_query_matches_both_youtube_and_local_text() -> None:
    comparison_items = [
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=1,
            local_song_id=4,
            comparison_status=ComparisonStatus.FOUND,
            youtube_title="Song One",
            youtube_artist="Artist One",
            local_title="Song One",
            local_artist="Artist One",
            score=99.0,
            reason="Coincidencia fuerte en titulo y artista.",
        ),
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=2,
            local_song_id=None,
            comparison_status=ComparisonStatus.MISSING,
            youtube_title="Lost Tape",
            youtube_artist="Rare Crew",
            local_title=None,
            local_artist=None,
            score=0.0,
            reason="No existe una candidata local con score minimo suficiente.",
        ),
    ]

    assert filterComparisonItemsByQuery(comparison_items, "rare crew") == [comparison_items[1]]
    assert filterComparisonItemsByQuery(comparison_items, "song one") == [comparison_items[0]]
    assert filterComparisonItemsByQuery(comparison_items, "score minimo") == [comparison_items[1]]
    assert filterComparisonItemsByQuery(comparison_items, "artist one") == [comparison_items[0]]


def test_filter_comparison_items_by_query_matches_local_title_or_artist_in_results() -> None:
    comparison_items = [
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=1,
            local_song_id=7,
            comparison_status=ComparisonStatus.POSSIBLE_MATCH,
            youtube_title="Numb Live",
            youtube_artist="Linkin Park",
            local_title="Numb",
            local_artist="Linkin Park Tribute",
            score=78.0,
            reason="Coincidencia parcial por variantes en el titulo.",
        ),
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=2,
            local_song_id=8,
            comparison_status=ComparisonStatus.FOUND,
            youtube_title="Faint",
            youtube_artist="Linkin Park",
            local_title="Faint",
            local_artist="Linkin Park",
            score=99.0,
            reason="Coincidencia fuerte en titulo y artista.",
        ),
    ]

    assert filterComparisonItemsByQuery(comparison_items, "tribute") == [comparison_items[0]]
    assert filterComparisonItemsByQuery(comparison_items, "numb") == [comparison_items[0]]


def test_filter_comparison_items_by_query_requires_all_tokens() -> None:
    comparison_items = [
        PlaylistComparisonItemResultDto(
            youtube_playlist_item_id=1,
            local_song_id=4,
            comparison_status=ComparisonStatus.POSSIBLE_MATCH,
            youtube_title="Song One Live",
            youtube_artist="Artist One",
            local_title="Song One",
            local_artist="Another Artist",
            score=61.0,
            reason="Coincidencia parcial detectada.",
        )
    ]

    assert filterComparisonItemsByQuery(comparison_items, "song another") == comparison_items
    assert filterComparisonItemsByQuery(comparison_items, "song missing-token") == []
