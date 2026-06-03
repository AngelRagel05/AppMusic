from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LocalFolder:
    id: int | None
    path: str
    display_name: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
