from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActivateLocalFolderInputDto:
    local_folder_id: int
