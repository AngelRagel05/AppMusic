from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImportYoutubePlaylistItemsResultDto:
    youtube_playlist_id: int
    playlist_title: str
    imported_item_count: int
    created_item_count: int = 0
    updated_item_count: int = 0
    existing_item_count: int = 0
    removed_item_count: int = 0
