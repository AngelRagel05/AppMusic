from __future__ import annotations

import pytest
from app.domain.playlists.entities.playlistComparisonResult import PlaylistComparisonResult
from app.shared.constants.comparison import ComparisonStatus


def test_playlist_comparison_result_allows_missing_without_local_song() -> None:
    result = PlaylistComparisonResult(
        playlist_comparison_id=1,
        youtube_playlist_item_id=2,
        local_song_id=None,
        match_status=ComparisonStatus.MISSING.value,
        score=0.0,
        matched_by="auto:no_competitive_candidate",
    )

    assert result.local_song_id is None


def test_playlist_comparison_result_rejects_missing_with_local_song() -> None:
    with pytest.raises(ValueError, match="missing"):
        PlaylistComparisonResult(
            playlist_comparison_id=1,
            youtube_playlist_item_id=2,
            local_song_id=9,
            match_status=ComparisonStatus.MISSING.value,
            score=0.0,
            matched_by="manual:user_marked_missing",
        )


def test_playlist_comparison_result_rejects_found_without_local_song() -> None:
    with pytest.raises(ValueError, match="found"):
        PlaylistComparisonResult(
            playlist_comparison_id=1,
            youtube_playlist_item_id=2,
            local_song_id=None,
            match_status=ComparisonStatus.FOUND.value,
            score=98.0,
            matched_by="manual:user_marked_found",
        )


def test_playlist_comparison_result_allows_possible_match_without_local_song() -> None:
    result = PlaylistComparisonResult(
        playlist_comparison_id=1,
        youtube_playlist_item_id=2,
        local_song_id=None,
        match_status=ComparisonStatus.POSSIBLE_MATCH.value,
        score=74.0,
        matched_by="auto:ambiguous",
    )

    assert result.match_status == ComparisonStatus.POSSIBLE_MATCH.value


def test_playlist_comparison_result_allows_legacy_matched_by_text() -> None:
    result = PlaylistComparisonResult(
        playlist_comparison_id=1,
        youtube_playlist_item_id=2,
        local_song_id=9,
        match_status=ComparisonStatus.FOUND.value,
        score=99.0,
        matched_by="Coincidencia confirmada por titulo y artista validos.",
    )

    assert result.matched_by == "Coincidencia confirmada por titulo y artista validos."


def test_playlist_comparison_result_rejects_unknown_matched_by_prefix() -> None:
    with pytest.raises(ValueError, match="prefijos controlados"):
        PlaylistComparisonResult(
            playlist_comparison_id=1,
            youtube_playlist_item_id=2,
            local_song_id=9,
            match_status=ComparisonStatus.FOUND.value,
            score=99.0,
            matched_by="user:free_text",
        )
