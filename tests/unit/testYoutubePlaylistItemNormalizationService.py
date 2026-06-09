from __future__ import annotations

import pytest

from app.domain.playlists.services import (
    NormalizedYoutubePlaylistItemMetadata,
    normalizeYoutubePlaylistItemMetadata,
)


def test_normalize_youtube_playlist_item_metadata_normalizes_simple_title() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="  My Song  ",
        raw_channel_name="  My Artist  ",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="my song",
        normalized_artist="my artist",
    )


def test_normalize_youtube_playlist_item_metadata_removes_decorative_noise() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="My Song (Official Video) [HD] 4K",
        raw_channel_name="My Artist",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="my song",
        normalized_artist="my artist",
    )


def test_normalize_youtube_playlist_item_metadata_extracts_artist_and_song_from_title() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="Kendrick Lamar - HUMBLE. (Official Video)",
        raw_channel_name="KendrickLamarVEVO",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="humble",
        normalized_artist="kendrick lamar",
    )


def test_normalize_youtube_playlist_item_metadata_uses_channel_name_as_artist_fallback() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="HUMBLE. (Lyrics)",
        raw_channel_name="  Kendrick Lamar  ",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="humble",
        normalized_artist="kendrick lamar",
    )


def test_normalize_youtube_playlist_item_metadata_extracts_artist_and_title_from_numbered_track() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="10. Space Hammu - I PROMISE ft. Raggio",
        raw_channel_name="Space Hammu",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="i promise",
        normalized_artist="space hammu",
    )


def test_normalize_youtube_playlist_item_metadata_extracts_title_and_artist_when_track_index_leads() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="02 - SINCERAMENTE - CHEB RUBËN",
        raw_channel_name="CHEB RUBËN",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="sinceramente",
        normalized_artist="cheb ruben",
    )


def test_normalize_youtube_playlist_item_metadata_extracts_artist_and_title_from_pipe_separator() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="NATOS | SELECTA Motorseries #01",
        raw_channel_name="Selecta",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="selecta motorseries 01",
        normalized_artist="natos",
    )


def test_normalize_youtube_playlist_item_metadata_removes_ignored_youtube_noise_from_title() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="Cruz Cafuné - Folelé ft. BOJ (Visualizer) [Letra]",
        raw_channel_name="Cruz Cafuné",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="folele",
        normalized_artist="cruz cafune",
    )


def test_normalize_youtube_playlist_item_metadata_does_not_treat_channel_contains_as_enough_to_flip_artist() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="NATOS | SELECTA Motorseries #01",
        raw_channel_name="Selecta Motorseries",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="selecta motorseries 01",
        normalized_artist="natos",
    )


def test_normalize_youtube_playlist_item_metadata_keeps_live_and_remix_when_they_are_real_title_content() -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title="Artist - My Song (Live Remix Version)",
        raw_channel_name="Artist",
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title="my song live remix version",
        normalized_artist="artist",
    )


@pytest.mark.parametrize(
    ("raw_title", "raw_channel_name", "expected_title", "expected_artist"),
    [
        (
            "CRUZ CAFUNÉ - Practice ft. HOKE (Visualizer)",
            "Cruz Cafuné",
            "practice",
            "cruz cafune",
        ),
        (
            "CRUZ CAFUNÉ - G WAGON ft. LA PANTERA (Visualizer)",
            "Cruz Cafuné",
            "g wagon",
            "cruz cafune",
        ),
        (
            "SFDK & Mama San - Éshate Pa Cá",
            "SFDK Oficial",
            "eshate pa ca",
            "sfdk mama san",
        ),
        (
            "SFDK & Abbi Fernández - Donde Duele Más",
            "SFDK Oficial",
            "donde duele mas",
            "sfdk abbi fernandez",
        ),
    ],
)
def test_normalize_youtube_playlist_item_metadata_handles_real_library_titles(
    raw_title: str,
    raw_channel_name: str,
    expected_title: str,
    expected_artist: str,
) -> None:
    normalized = normalizeYoutubePlaylistItemMetadata(
        raw_title=raw_title,
        raw_channel_name=raw_channel_name,
    )

    assert normalized == NormalizedYoutubePlaylistItemMetadata(
        normalized_title=expected_title,
        normalized_artist=expected_artist,
    )
