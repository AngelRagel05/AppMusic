from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateYoutubePlaylistInputDto:
    youtube_playlist_id: int
    playlist_url: str
    title: str
