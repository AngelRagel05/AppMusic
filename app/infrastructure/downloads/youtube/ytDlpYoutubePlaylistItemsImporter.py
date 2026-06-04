from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qs, urlparse

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.application.dto.importedYoutubePlaylistItemDto import ImportedYoutubePlaylistItemDto
from app.application.use_cases.playlists.youtubePlaylistItemsImporterPort import (
    YoutubePlaylistImportExtractorError,
    YoutubePlaylistImportInvalidUrlError,
    YoutubePlaylistItemsImporterPort,
    YoutubePlaylistNotAccessibleError,
)
from app.shared.constants.youtube import (
    CANONICAL_YOUTUBE_PLAYLIST_URL,
    VALID_YOUTUBE_HOSTS,
)


class YtDlpYoutubePlaylistItemsImporter(YoutubePlaylistItemsImporterPort):
    def importItems(
        self,
        *,
        playlist_url: str,
        external_playlist_id: str,
    ) -> list[ImportedYoutubePlaylistItemDto]:
        resolved_playlist_url = self._resolvePlaylistUrl(
            playlist_url=playlist_url,
            external_playlist_id=external_playlist_id,
        )
        options = {
            "extract_flat": True,
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "playlistend": None,
        }

        try:
            with YoutubeDL(options) as youtube_dl:
                extracted_info = youtube_dl.extract_info(
                    resolved_playlist_url,
                    download=False,
                )
        except DownloadError as error:
            raise self._mapDownloadError(error) from error
        except Exception as error:
            raise YoutubePlaylistImportExtractorError(
                f"Fallo inesperado al importar items de la playlist: {error}"
            ) from error

        entries = extracted_info.get("entries")
        if not isinstance(entries, list):
            raise YoutubePlaylistNotAccessibleError(
                "La playlist indicada no devolvio una lista valida de items."
            )

        return [
            self._mapEntryToDto(entry, fallback_position=index)
            for index, entry in enumerate(entries, start=1)
            if isinstance(entry, dict)
        ]

    def _resolvePlaylistUrl(
        self,
        *,
        playlist_url: str,
        external_playlist_id: str,
    ) -> str:
        normalized_playlist_url = playlist_url.strip()
        normalized_external_playlist_id = external_playlist_id.strip()

        if normalized_playlist_url:
            playlist_id = self._extractPlaylistIdFromUrl(normalized_playlist_url)
            return CANONICAL_YOUTUBE_PLAYLIST_URL.format(playlist_id=playlist_id)

        if normalized_external_playlist_id:
            return CANONICAL_YOUTUBE_PLAYLIST_URL.format(
                playlist_id=normalized_external_playlist_id
            )

        raise YoutubePlaylistImportInvalidUrlError(
            "Hace falta una URL de playlist valida o un external_playlist_id."
        )

    def _extractPlaylistIdFromUrl(self, playlist_url: str) -> str:
        parsed_url = urlparse(playlist_url)
        if parsed_url.scheme not in {"http", "https"}:
            raise YoutubePlaylistImportInvalidUrlError(
                "La URL de la playlist debe empezar por http o https."
            )

        host = parsed_url.netloc.lower()
        if host not in VALID_YOUTUBE_HOSTS:
            raise YoutubePlaylistImportInvalidUrlError(
                "La URL indicada no pertenece a YouTube."
            )

        playlist_ids = parse_qs(parsed_url.query).get("list", [])
        playlist_id = playlist_ids[0].strip() if playlist_ids else ""
        if not playlist_id:
            raise YoutubePlaylistImportInvalidUrlError(
                "La URL de la playlist debe incluir el parametro list."
            )

        return playlist_id

    def _mapDownloadError(self, error: DownloadError) -> Exception:
        message = str(error)
        normalized_message = message.lower()

        if (
            "unsupported url" in normalized_message
            or "not a valid url" in normalized_message
            or "url could be a direct video link" in normalized_message
        ):
            return YoutubePlaylistImportInvalidUrlError(message)

        if (
            "private" in normalized_message
            or "not available" in normalized_message
            or "unavailable" in normalized_message
            or "does not exist" in normalized_message
            or "inaccessible" in normalized_message
            or "playlist could not be found" in normalized_message
        ):
            return YoutubePlaylistNotAccessibleError(message)

        return YoutubePlaylistImportExtractorError(message)

    def _mapEntryToDto(
        self,
        entry: dict[str, Any],
        *,
        fallback_position: int,
    ) -> ImportedYoutubePlaylistItemDto:
        raw_channel_name = (
            entry.get("channel")
            or entry.get("uploader")
            or entry.get("artist")
            or ""
        )

        return ImportedYoutubePlaylistItemDto(
            external_video_id=str(entry.get("id") or "").strip(),
            position=self._extractPosition(entry, fallback_position=fallback_position),
            raw_title=str(entry.get("title") or "").strip(),
            raw_channel_name=str(raw_channel_name).strip(),
            duration_seconds=self._extractDuration(entry),
            published_at=self._extractPublishedAt(entry),
        )

    def _extractPosition(
        self,
        entry: dict[str, Any],
        *,
        fallback_position: int,
    ) -> int:
        playlist_index = entry.get("playlist_index")
        if isinstance(playlist_index, int) and playlist_index > 0:
            return playlist_index
        return fallback_position

    def _extractDuration(self, entry: dict[str, Any]) -> float | None:
        duration = entry.get("duration")
        if isinstance(duration, (int, float)) and duration >= 0:
            return float(duration)
        return None

    def _extractPublishedAt(self, entry: dict[str, Any]) -> datetime | None:
        upload_date = entry.get("upload_date")
        if not isinstance(upload_date, str) or len(upload_date) != 8 or not upload_date.isdigit():
            return None

        try:
            parsed_date = datetime.strptime(upload_date, "%Y%m%d")
        except ValueError:
            return None

        return parsed_date.replace(tzinfo=UTC)
