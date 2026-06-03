from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateIgnoredTermInputDto:
    term: str
    scope: str
    language: str
