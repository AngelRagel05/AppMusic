from __future__ import annotations

from datetime import UTC, datetime

import pytest
from yt_dlp.utils import DownloadError

from app.application.dto.importedYoutubePlaylistItemDto import ImportedYoutubePlaylistItemDto
from app.application.use_cases.playlists import (
    YoutubePlaylistImportExtractorError,
    YoutubePlaylistImportInvalidUrlError,
    YoutubePlaylistNotAccessibleError,
)
from app.infrastructure.downloads.youtube import YtDlpYoutubePlaylistItemsImporter


class YoutubeDLStub:
    extracted_info: dict | None = None
    raised_error: Exception | None = None
    received_url: str | None = None
    received_download: bool | None = None
    received_options: dict | None = None

    def __init__(self, options: dict) -> None:
        YoutubeDLStub.received_options = options

    def __enter__(self) -> YoutubeDLStub:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def extract_info(self, url: str, download: bool) -> dict:
        YoutubeDLStub.received_url = url
        YoutubeDLStub.received_download = download
        if YoutubeDLStub.raised_error is not None:
            raise YoutubeDLStub.raised_error
        if YoutubeDLStub.extracted_info is None:
            raise AssertionError("El stub necesita extracted_info o raised_error.")
        return YoutubeDLStub.extracted_info


def resetYoutubeDLStub() -> None:
    YoutubeDLStub.extracted_info = None
    YoutubeDLStub.raised_error = None
    YoutubeDLStub.received_url = None
    YoutubeDLStub.received_download = None
    YoutubeDLStub.received_options = None


def test_importItems_maps_playlist_entries_to_dtos(monkeypatch: pytest.MonkeyPatch) -> None:
    resetYoutubeDLStub()
    YoutubeDLStub.extracted_info = {
        "entries": [
            {
                "id": "abc123",
                "playlist_index": 4,
                "title": "Song One",
                "channel": "Artist One",
                "duration": 185,
                "upload_date": "20240601",
            },
            {
                "id": "def456",
                "title": "Song Two",
                "uploader": "Artist Two",
            },
        ]
    }
    monkeypatch.setattr(
        "app.infrastructure.downloads.youtube.ytDlpYoutubePlaylistItemsImporter.YoutubeDL",
        YoutubeDLStub,
    )
    importer = YtDlpYoutubePlaylistItemsImporter()

    imported_items = importer.importItems(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
    )

    assert YoutubeDLStub.received_url == "https://www.youtube.com/playlist?list=PL123"
    assert YoutubeDLStub.received_download is False
    assert imported_items == [
        ImportedYoutubePlaylistItemDto(
            external_video_id="abc123",
            position=4,
            raw_title="Song One",
            raw_channel_name="Artist One",
            duration_seconds=185.0,
            published_at=datetime(2024, 6, 1, tzinfo=UTC),
        ),
        ImportedYoutubePlaylistItemDto(
            external_video_id="def456",
            position=2,
            raw_title="Song Two",
            raw_channel_name="Artist Two",
            duration_seconds=None,
            published_at=None,
        ),
    ]


def test_importItems_builds_canonical_url_from_external_playlist_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resetYoutubeDLStub()
    YoutubeDLStub.extracted_info = {"entries": []}
    monkeypatch.setattr(
        "app.infrastructure.downloads.youtube.ytDlpYoutubePlaylistItemsImporter.YoutubeDL",
        YoutubeDLStub,
    )
    importer = YtDlpYoutubePlaylistItemsImporter()

    importer.importItems(
        playlist_url="",
        external_playlist_id="PLXYZ",
    )

    assert YoutubeDLStub.received_url == "https://www.youtube.com/playlist?list=PLXYZ"


def test_importItems_translates_invalid_url_error_before_calling_extractor() -> None:
    importer = YtDlpYoutubePlaylistItemsImporter()

    with pytest.raises(YoutubePlaylistImportInvalidUrlError, match="no pertenece a YouTube"):
        importer.importItems(
            playlist_url="https://open.spotify.com/playlist/123",
            external_playlist_id="",
        )


def test_importItems_translates_not_accessible_download_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resetYoutubeDLStub()
    YoutubeDLStub.raised_error = DownloadError("ERROR: Private video. Sign in if you've been granted access to this video")
    monkeypatch.setattr(
        "app.infrastructure.downloads.youtube.ytDlpYoutubePlaylistItemsImporter.YoutubeDL",
        YoutubeDLStub,
    )
    importer = YtDlpYoutubePlaylistItemsImporter()

    with pytest.raises(YoutubePlaylistNotAccessibleError, match="Private video"):
        importer.importItems(
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
        )


def test_importItems_translates_unexpected_download_error_to_extractor_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resetYoutubeDLStub()
    YoutubeDLStub.raised_error = DownloadError("ERROR: extractor exploded")
    monkeypatch.setattr(
        "app.infrastructure.downloads.youtube.ytDlpYoutubePlaylistItemsImporter.YoutubeDL",
        YoutubeDLStub,
    )
    importer = YtDlpYoutubePlaylistItemsImporter()

    with pytest.raises(YoutubePlaylistImportExtractorError, match="extractor exploded"):
        importer.importItems(
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
        )
