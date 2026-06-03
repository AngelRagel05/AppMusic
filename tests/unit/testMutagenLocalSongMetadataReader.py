from __future__ import annotations

from types import SimpleNamespace

from mutagen import MutagenError

from app.infrastructure.metadata.mutagenLocalSongMetadataReader import (
    MutagenLocalSongMetadataReader,
)


def test_readMetadata_returns_extracted_values(monkeypatch) -> None:
    reader = MutagenLocalSongMetadataReader()

    class FakeAudioFile:
        def get(self, key: str, default):
            values = {
                "title": ["Numb"],
                "artist": ["Linkin Park"],
                "album": ["Meteora"],
                "date": ["2003-03-25"],
                "tracknumber": ["13/13"],
            }
            return values.get(key, default)

    monkeypatch.setattr(
        "app.infrastructure.metadata.mutagenLocalSongMetadataReader.MutagenFile",
        lambda _filePath, easy=True: FakeAudioFile(),
    )
    monkeypatch.setattr(
        "app.infrastructure.metadata.mutagenLocalSongMetadataReader.MP3",
        lambda _filePath: SimpleNamespace(info=SimpleNamespace(length=185.4)),
    )

    metadata = reader.readMetadata(r"C:\Music\LinkinPark\numb.mp3")

    assert metadata.title == "Numb"
    assert metadata.artist == "Linkin Park"
    assert metadata.album == "Meteora"
    assert metadata.release_year == 2003
    assert metadata.track_number_album == 13
    assert metadata.duration_seconds == 185.4


def test_readMetadata_returns_fallback_values_when_mutagen_fails(monkeypatch) -> None:
    reader = MutagenLocalSongMetadataReader()

    def raiseMutagenError(_filePath, easy=True):
        raise MutagenError("broken file")

    monkeypatch.setattr(
        "app.infrastructure.metadata.mutagenLocalSongMetadataReader.MutagenFile",
        raiseMutagenError,
    )

    metadata = reader.readMetadata(r"C:\Music\Broken\songFallback.mp3")

    assert metadata.title == "songFallback"
    assert metadata.artist == ""
    assert metadata.album == ""
    assert metadata.release_year == 0
    assert metadata.track_number_album == 0
    assert metadata.duration_seconds == 0.0
