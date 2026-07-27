from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.localSongDto import LocalSongDto


@dataclass(frozen=True, slots=True)
class PagedLocalSongsDto:
    items: list[LocalSongDto]
    total: int
    page: int
    page_size: int
