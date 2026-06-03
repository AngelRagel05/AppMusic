from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeleteLocalFolderInputDto:
    local_folder_id: int
