from __future__ import annotations

from app.domain.metadata.services import (
    NormalizedMusicComparisonMetadata,
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
    normalizeMusicComparisonTitle,
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


def test_normalize_music_comparison_text_removes_accents_topic_and_video_noise() -> None:
    normalized = normalizeMusicComparisonText("BIZARRAP Topic - Frío (Video Oficial)")

    assert normalized == "bizarrap frio"


def test_normalize_music_comparison_title_removes_track_numbers_and_feature_suffix() -> None:
    normalized = normalizeMusicComparisonTitle("10. Space Hammu - I PROMISE ft. Raggio")

    assert normalized == "space hammu i promise"


def test_normalize_music_comparison_artist_removes_leading_track_numbers() -> None:
    normalized = normalizeMusicComparisonArtist("10. Space Hammu")

    assert normalized == "space hammu"
