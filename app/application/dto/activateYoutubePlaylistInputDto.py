from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActivateYoutubePlaylistInputDto:
    youtube_playlist_id: int
