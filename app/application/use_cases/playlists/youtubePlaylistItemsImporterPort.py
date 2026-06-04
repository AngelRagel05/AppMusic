from __future__ import annotations

from typing import Protocol

from app.application.dto.importedYoutubePlaylistItemDto import ImportedYoutubePlaylistItemDto


class YoutubePlaylistItemsImporterPort(Protocol):
    def importItems(
        self,
        *,
        playlist_url: str,
        external_playlist_id: str,
    ) -> list[ImportedYoutubePlaylistItemDto]:
        ...


class YoutubePlaylistImportError(Exception):
    """Base error for YouTube playlist item import failures."""


class YoutubePlaylistNotAccessibleError(YoutubePlaylistImportError):
    """Raised when the target playlist cannot be accessed or resolved."""


class YoutubePlaylistImportInvalidUrlError(YoutubePlaylistImportError):
    """Raised when the importer receives an invalid YouTube playlist URL."""


class YoutubePlaylistImportExtractorError(YoutubePlaylistImportError):
    """Raised when the external extractor fails unexpectedly."""
