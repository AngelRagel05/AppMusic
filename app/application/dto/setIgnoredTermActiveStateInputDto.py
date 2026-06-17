from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SetIgnoredTermActiveStateInputDto:
    term_id: int
    is_active: bool
