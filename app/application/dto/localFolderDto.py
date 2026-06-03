from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalFolderDto:
    id: int
    path: str
    display_name: str
    is_active: bool
