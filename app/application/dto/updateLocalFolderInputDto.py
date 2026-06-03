from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateLocalFolderInputDto:
    local_folder_id: int
    path: str
