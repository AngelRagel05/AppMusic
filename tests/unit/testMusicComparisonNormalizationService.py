from __future__ import annotations

import pytest

from app.domain.metadata.services import (
    COMPARISON_IGNORED_TERMS,
    NormalizedMusicComparisonMetadata,
    normalizeMusicComparisonAlbum,
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
    normalizeMusicComparisonTitle,
    splitMusicComparisonSegments,
)


def test_normalize_music_comparison_text_normalizes_clean_title() -> None:
    normalized = normalizeMusicComparisonText("  My Song  ")

    assert normalized == "my song"


def test_normalize_music_comparison_text_removes_decorative_noise() -> None:
    normalized = normalizeMusicComparisonText("My Song (Official Video) [HD] 4K")

    assert normalized == "my song"


def test_normalize_music_comparison_metadata_normalizes_artist_variants() -> None:
    normalized = normalizeMusicComparisonMetadata(
        title="Song Name",
        artist="  ARTIST_NAME:OFFICIAL  ",
    )

    assert normalized == NormalizedMusicComparisonMetadata(
        normalized_title="song name",
        normalized_artist="artist name",
        ignored_artist_decorators=("official",),
    )


def test_normalize_music_comparison_metadata_keeps_album_as_optional_signal() -> None:
    normalized = normalizeMusicComparisonMetadata(
        title="Song Name feat. Guest",
        artist="Artist Name feat. Guest",
        album="My Album (Official Audio)",
    )

    assert normalized == NormalizedMusicComparisonMetadata(
        normalized_title="song name",
        normalized_artist="artist name guest",
        normalized_album="my album",
        title_collaborators=("guest",),
        artist_collaborators=("guest",),
    )


def test_normalize_music_comparison_text_returns_empty_string_for_empty_input() -> None:
    normalized = normalizeMusicComparisonText("  (Official) [HD]  ")

    assert normalized == ""


def test_normalize_music_comparison_text_removes_accents_topic_and_video_noise() -> None:
    normalized = normalizeMusicComparisonText("BIZARRAP Topic - Frío (Video Oficial)")

    assert normalized == "bizarrap frio"


def test_normalize_music_comparison_title_removes_track_numbers_and_feature_suffix() -> None:
    normalized = normalizeMusicComparisonTitle("10. Space Hammu - I PROMISE ft. Raggio")

    assert normalized == "space hammu i promise"


def test_normalize_music_comparison_artist_removes_leading_track_numbers() -> None:
    normalized = normalizeMusicComparisonArtist("10. Space Hammu")

    assert normalized == "space hammu"


def test_normalize_music_comparison_text_does_not_remove_remix_live_or_version() -> None:
    normalized = normalizeMusicComparisonText("My Song (Live Version Remix)")

    assert normalized == "my song live version remix"


def test_split_music_comparison_segments_uses_single_separator_policy() -> None:
    segments = splitMusicComparisonSegments("Artist /// Song | Demo - 2024")

    assert segments == ("Artist", "Song", "Demo", "2024")


def test_comparison_ignored_terms_include_base_business_terms() -> None:
    assert {"ft", "feat", "featuring", "prod", "official", "audio", "visualizer", "topic", "lyrics", "letra", "vol"} <= set(
        COMPARISON_IGNORED_TERMS
    )


def test_normalize_music_comparison_album_reuses_comparison_policy() -> None:
    normalized = normalizeMusicComparisonAlbum("Mi Album [Official Audio]")

    assert normalized == "mi album"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Folelé ft. BOJ", "folele"),
        ("Practice ft. HOKE", "practice"),
        ("G WAGON ft. LA PANTERA", "g wagon"),
        ("Éshate Pa Cá", "eshate pa ca"),
        ("Donde Duele Más", "donde duele mas"),
        ("Platos Rotos", "platos rotos"),
    ],
)
def test_normalize_music_comparison_title_handles_real_regression_cases(
    value: str,
    expected: str,
) -> None:
    assert normalizeMusicComparisonTitle(value) == expected


def test_normalize_music_comparison_metadata_keeps_inconsistent_artist_as_separate_signal() -> None:
    normalized = normalizeMusicComparisonMetadata(
        title="Platos Rotos",
        artist="Otro Artista",
    )

    assert normalized == NormalizedMusicComparisonMetadata(
        normalized_title="platos rotos",
        normalized_artist="otro artista",
    )


def test_normalize_music_comparison_title_ignores_vol_symmetrically_for_local_metadata() -> None:
    normalized = normalizeMusicComparisonTitle("Otra vez Vol. 4")

    assert normalized == "otra vez 4"
