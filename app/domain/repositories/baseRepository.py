from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class BaseRepository[EntityType, IdType](ABC):
    @abstractmethod
    def get_by_id(self, entity_id: IdType) -> EntityType | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Sequence[EntityType]:
        raise NotImplementedError

    @abstractmethod
    def add(self, entity: EntityType) -> EntityType:
        raise NotImplementedError

    @abstractmethod
    def remove(self, entity: EntityType) -> None:
        raise NotImplementedError
