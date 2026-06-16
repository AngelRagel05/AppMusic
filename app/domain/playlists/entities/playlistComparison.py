from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PlaylistComparison:
    id: int | None = None
    youtube_playlist_id: int = 0
    local_folder_id: int = 0
    compared_at: datetime | None = None
    youtube_playlist_imported_at: datetime | None = None
    local_library_scanned_at: datetime | None = None
    youtube_playlist_state_fingerprint: str | None = None
    local_library_state_fingerprint: str | None = None
    ignored_terms_version: str | None = None
    matching_rules_version: str | None = None
    created_at: datetime | None = None
