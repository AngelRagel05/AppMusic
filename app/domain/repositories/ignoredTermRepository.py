from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.entities.ignoredTerm import IgnoredTerm


class IgnoredTermRepository(ABC):
    @abstractmethod
    def list_all(self) -> Sequence[IgnoredTerm]:
        raise NotImplementedError

    @abstractmethod
    def create(self, term: str, scope: str, language: str) -> IgnoredTerm:
        raise NotImplementedError

    @abstractmethod
    def update(self, term_id: int, term: str, scope: str, language: str) -> IgnoredTerm:
        raise NotImplementedError

    @abstractmethod
    def delete(self, term_id: int) -> None:
        raise NotImplementedError
