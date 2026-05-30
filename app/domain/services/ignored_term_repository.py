from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.entities.ignored_term import IgnoredTerm


class IgnoredTermRepository(ABC):
    @abstractmethod
    def list_all(self) -> Sequence[IgnoredTerm]:
        raise NotImplementedError

    @abstractmethod
    def create(self, term: str, scope: str, language: str) -> IgnoredTerm:
        raise NotImplementedError
