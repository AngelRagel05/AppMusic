from __future__ import annotations

from collections.abc import Iterable

from app.application.dto.importYoutubePlaylistItemsResultDto import (
    ImportYoutubePlaylistItemsResultDto,
)
from app.application.use_cases.playlists.youtubePlaylistItemsImporterPort import (
    YoutubePlaylistItemsImporterPort,
)
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.domain.playlists.services import normalizeYoutubePlaylistItemMetadata


class ImportYoutubePlaylistItemsUseCase:
    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        youtube_playlist_item_repository: YoutubePlaylistItemRepository,
        youtube_playlist_items_importer: YoutubePlaylistItemsImporterPort,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._youtube_playlist_item_repository = youtube_playlist_item_repository
        self._youtube_playlist_items_importer = youtube_playlist_items_importer

    def execute(self) -> ImportYoutubePlaylistItemsResultDto:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        if active_youtube_playlist is None or active_youtube_playlist.id is None:
            raise ValueError("No hay una playlist principal activa para importar.")

        persisted_snapshot = self._youtube_playlist_item_repository.list_by_playlist(
            active_youtube_playlist.id
        )
        imported_items = self._youtube_playlist_items_importer.importItems(
            playlist_url=active_youtube_playlist.playlist_url,
            external_playlist_id=active_youtube_playlist.external_playlist_id,
        )
        youtube_playlist_items = [
            self._buildYoutubePlaylistItem(
                youtube_playlist_id=active_youtube_playlist.id,
                imported_item=imported_item,
            )
            for imported_item in imported_items
        ]
        change_summary = self._buildChangeSummary(
            persisted_snapshot=persisted_snapshot,
            imported_snapshot=youtube_playlist_items,
        )
        persisted_items = self._youtube_playlist_item_repository.replace_for_playlist(
            active_youtube_playlist.id,
            youtube_playlist_items,
        )

        return ImportYoutubePlaylistItemsResultDto(
            youtube_playlist_id=active_youtube_playlist.id,
            playlist_title=active_youtube_playlist.title,
            imported_item_count=len(persisted_items),
            created_item_count=change_summary["created_item_count"],
            updated_item_count=change_summary["updated_item_count"],
            existing_item_count=change_summary["existing_item_count"],
            removed_item_count=change_summary["removed_item_count"],
        )

    def _buildYoutubePlaylistItem(
        self,
        *,
        youtube_playlist_id: int,
        imported_item,
    ) -> YoutubePlaylistItem:
        normalized_metadata = normalizeYoutubePlaylistItemMetadata(
            raw_title=imported_item.raw_title,
            raw_channel_name=imported_item.raw_channel_name,
        )
        return YoutubePlaylistItem(
            id=None,
            youtube_playlist_id=youtube_playlist_id,
            external_video_id=imported_item.external_video_id,
            position=imported_item.position,
            raw_title=imported_item.raw_title,
            raw_channel_name=imported_item.raw_channel_name,
            normalized_title=normalized_metadata.normalized_title,
            normalized_artist=normalized_metadata.normalized_artist,
            duration_seconds=imported_item.duration_seconds,
            published_at=imported_item.published_at,
        )

    def _buildChangeSummary(
        self,
        *,
        persisted_snapshot: Iterable[YoutubePlaylistItem],
        imported_snapshot: Iterable[YoutubePlaylistItem],
    ) -> dict[str, int]:
        persisted_items_by_external_video_id = {
            item.external_video_id: item for item in persisted_snapshot
        }
        imported_items_by_external_video_id = {
            item.external_video_id: item for item in imported_snapshot
        }

        created_item_count = 0
        updated_item_count = 0
        existing_item_count = 0

        for external_video_id, imported_item in imported_items_by_external_video_id.items():
            persisted_item = persisted_items_by_external_video_id.get(external_video_id)
            if persisted_item is None:
                created_item_count += 1
                continue

            if self._hasItemChanged(persisted_item, imported_item):
                updated_item_count += 1
                continue

            existing_item_count += 1

        removed_item_count = len(
            set(persisted_items_by_external_video_id)
            - set(imported_items_by_external_video_id)
        )

        return {
            "created_item_count": created_item_count,
            "updated_item_count": updated_item_count,
            "existing_item_count": existing_item_count,
            "removed_item_count": removed_item_count,
        }

    def _hasItemChanged(
        self,
        persisted_item: YoutubePlaylistItem,
        imported_item: YoutubePlaylistItem,
    ) -> bool:
        return (
            persisted_item.position != imported_item.position
            or persisted_item.raw_title != imported_item.raw_title
            or persisted_item.raw_channel_name != imported_item.raw_channel_name
            or persisted_item.normalized_title != imported_item.normalized_title
            or persisted_item.normalized_artist != imported_item.normalized_artist
            or persisted_item.duration_seconds != imported_item.duration_seconds
            or persisted_item.published_at != imported_item.published_at
        )
