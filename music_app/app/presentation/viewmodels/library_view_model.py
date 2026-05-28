from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LibraryViewModel:
    status_message: str = "Ready"

