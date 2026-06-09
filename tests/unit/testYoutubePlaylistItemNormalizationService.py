from __future__ import annotations

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
