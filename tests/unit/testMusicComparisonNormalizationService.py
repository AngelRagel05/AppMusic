from __future__ import annotations

from app.domain.metadata.services import (
    NormalizedMusicComparisonMetadata,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
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
    )


def test_normalize_music_comparison_text_returns_empty_string_for_empty_input() -> None:
    normalized = normalizeMusicComparisonText("  (Official) [HD]  ")

    assert normalized == ""
