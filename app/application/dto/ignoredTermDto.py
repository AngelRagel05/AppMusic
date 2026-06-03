from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IgnoredTermDto:
    id: int
    term: str
    scope: str
    language: str
    is_active: bool
