from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateIgnoredTermInputDto:
    term_id: int
    term: str
    scope: str
    language: str
