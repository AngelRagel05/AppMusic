from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DefineMainLocalFolderInputDto:
    path: str
    display_name: str = ""
