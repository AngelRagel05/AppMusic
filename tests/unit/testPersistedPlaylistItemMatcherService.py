from __future__ import annotations

import app.domain.playlists.services.persistedPlaylistItemMatcherService as matcher_service
from app.domain.playlists.services import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
    matchPersistedPlaylistItemToLocalSongs,
)
from app.shared.constants.comparison import ComparisonStatus


def test_match_persisted_playlist_item_to_local_songs_returns_found_for_clear_match() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=181.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 4
    assert result.comparison_status is ComparisonStatus.FOUND
    assert result.score >= 95.0


def test_match_persisted_playlist_item_to_local_songs_returns_missing_without_viable_candidate() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=181.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="totally different",
                artist="another artist",
                duration_seconds=240.0,
            )
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.score == 0.0


def test_match_persisted_playlist_item_to_local_songs_resolves_close_top_candidates_by_duration() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one ft guest a",
                duration_seconds=180.1,
            ),
            ComparableLocalSong(
                id=9,
                title="song one",
                artist="artist one ft guest b",
                duration_seconds=180.8,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 4
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_persisted_playlist_item_to_local_songs_returns_possible_for_real_ambiguity() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one ft guest a",
                duration_seconds=180.4,
            ),
            ComparableLocalSong(
                id=9,
                title="song one",
                artist="artist one ft guest b",
                duration_seconds=180.5,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert result.reason == "Ambiguedad entre dos candidatas plausibles."


def test_match_persisted_playlist_item_to_local_songs_returns_found_for_nadal015_case() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=18,
            normalized_title="memories i",
            normalized_artist="nadal015",
            duration_seconds=176.0,
        ),
        [
            ComparableLocalSong(
                id=19,
                title="memories i",
                artist="nadal015",
                duration_seconds=175.848,
            )
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 19
    assert result.comparison_status is ComparisonStatus.FOUND


def test_match_persisted_playlist_item_to_local_songs_returns_missing_for_exact_title_with_inconsistent_artist() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=50,
            normalized_title="platos rotos",
            normalized_artist="natos y waor",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=51,
                title="platos rotos",
                artist="otro artista",
                duration_seconds=180.4,
            )
        ],
    )

    assert result.local_song is None
    assert result.comparison_status is ComparisonStatus.MISSING
    assert result.reason == "Titulo competitivo pero artista inconsistente."


def test_match_persisted_playlist_item_to_local_songs_returns_possible_for_exact_title_without_artist_and_duration_over_1s() -> None:
    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=62,
            normalized_title="cancion exacta",
            normalized_artist="canal ruido",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=63,
                title="cancion exacta",
                artist="",
                duration_seconds=182.0,
            )
        ],
    )

    assert result.local_song is not None
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert result.reason == "Titulo exacto pero artista inconsistente."


def test_match_persisted_playlist_item_to_local_songs_cuts_early_for_clear_match(monkeypatch) -> None:
    score_calls: list[int] = []
    original_score_candidate = matcher_service._scoreCandidate

    def spy_score_candidate(*args, **kwargs):
        local_song = args[1]
        score_calls.append(local_song.id)
        return original_score_candidate(*args, **kwargs)

    monkeypatch.setattr(matcher_service, "_scoreCandidate", spy_score_candidate)

    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=9,
                title="totally different",
                artist="another artist",
                duration_seconds=220.0,
            ),
            ComparableLocalSong(
                id=15,
                title="other song",
                artist="other artist",
                duration_seconds=200.0,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.local_song.id == 4
    assert result.comparison_status is ComparisonStatus.FOUND
    assert score_calls == [4]


def test_match_persisted_playlist_item_to_local_songs_does_not_cut_early_for_medium_artist(monkeypatch) -> None:
    score_calls: list[int] = []
    original_score_candidate = matcher_service._scoreCandidate

    def spy_score_candidate(*args, **kwargs):
        local_song = args[1]
        score_calls.append(local_song.id)
        return original_score_candidate(*args, **kwargs)

    monkeypatch.setattr(matcher_service, "_scoreCandidate", spy_score_candidate)

    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist 1",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=9,
                title="other song",
                artist="other artist",
                duration_seconds=220.0,
            ),
        ],
    )

    assert result.comparison_status in (
        ComparisonStatus.FOUND,
        ComparisonStatus.MISSING,
        ComparisonStatus.POSSIBLE_MATCH,
    )
    assert score_calls == [4, 9]


def test_match_persisted_playlist_item_to_local_songs_does_not_cut_early_for_only_acceptable_title(monkeypatch) -> None:
    score_calls: list[int] = []
    original_score_candidate = matcher_service._scoreCandidate

    def spy_score_candidate(*args, **kwargs):
        local_song = args[1]
        score_calls.append(local_song.id)
        return original_score_candidate(*args, **kwargs)

    monkeypatch.setattr(matcher_service, "_scoreCandidate", spy_score_candidate)

    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one live",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=9,
                title="other song",
                artist="other artist",
                duration_seconds=220.0,
            ),
        ],
    )

    assert result.comparison_status in (
        ComparisonStatus.FOUND,
        ComparisonStatus.MISSING,
        ComparisonStatus.POSSIBLE_MATCH,
    )
    assert score_calls == [4, 9]


def test_match_persisted_playlist_item_to_local_songs_does_not_cut_early_when_real_tie_is_possible(monkeypatch) -> None:
    score_calls: list[int] = []
    original_score_candidate = matcher_service._scoreCandidate

    def spy_score_candidate(*args, **kwargs):
        local_song = args[1]
        score_calls.append(local_song.id)
        return original_score_candidate(*args, **kwargs)

    monkeypatch.setattr(matcher_service, "_scoreCandidate", spy_score_candidate)

    result = matchPersistedPlaylistItemToLocalSongs(
        ComparableYoutubePlaylistItem(
            id=1,
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        ),
        [
            ComparableLocalSong(
                id=4,
                title="song one",
                artist="artist one",
                duration_seconds=180.0,
            ),
            ComparableLocalSong(
                id=9,
                title="song one",
                artist="artist one",
                duration_seconds=180.2,
            ),
        ],
    )

    assert result.local_song is not None
    assert result.comparison_status is ComparisonStatus.POSSIBLE_MATCH
    assert score_calls == [4, 9]
