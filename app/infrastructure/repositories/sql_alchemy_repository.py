from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.infrastructure.database.base import Base


class SqlAlchemyRepository[ModelType: Base, IdType]:
    def __init__(self, session: Session, model_type: type[ModelType]) -> None:
        self._session = session
        self._model_type = model_type

    def get_by_id(self, entity_id: IdType) -> ModelType | None:
        return self._session.get(self._model_type, entity_id)

    def list_all(self) -> Sequence[ModelType]:
        statement: Select[tuple[ModelType]] = select(self._model_type)
        return list(self._session.scalars(statement).all())

    def add(self, entity: ModelType) -> ModelType:
        self._session.add(entity)
        self._session.flush()
        return entity

    def remove(self, entity: ModelType) -> None:
        self._session.delete(entity)
        self._session.flush()
