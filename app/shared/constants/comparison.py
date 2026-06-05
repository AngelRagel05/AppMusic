from __future__ import annotations

from enum import StrEnum


class ComparisonStatus(StrEnum):
    FOUND = "found"
    MISSING = "missing"
    POSSIBLE_MATCH = "possible_match"
