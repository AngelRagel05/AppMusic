from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IgnoredTerm:
    id: int | None
    term: str
    scope: str
    language: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
