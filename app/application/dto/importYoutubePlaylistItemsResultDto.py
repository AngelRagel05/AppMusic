from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImportYoutubePlaylistItemsResultDto:
    youtube_playlist_id: int
    playlist_title: str
    imported_item_count: int
