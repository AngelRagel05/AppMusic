from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DownloadedAudioDto:
    file_path: str
    title: str
    artist: str
