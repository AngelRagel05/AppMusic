from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DefineMainYoutubePlaylistInputDto:
    playlist_url: str
