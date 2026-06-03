from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.filters.entities.ignoredTerm import IgnoredTerm
from app.domain.filters.repositories.ignoredTermRepository import IgnoredTermRepository
from app.infrastructure.database.models import IgnoredTerm as IgnoredTermModel


class IgnoredTermSqlAlchemyRepository(IgnoredTermRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> Sequence[IgnoredTerm]:
        statement: Select[tuple[IgnoredTermModel]] = select(IgnoredTermModel).order_by(
            IgnoredTermModel.term.asc(),
            IgnoredTermModel.scope.asc(),
            IgnoredTermModel.language.asc(),
        )
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def create(self, term: str, scope: str, language: str) -> IgnoredTerm:
        model = IgnoredTermModel(
            term=term,
            scope=scope,
            language=language,
            is_active=True,
        )
        self._session.add(model)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            msg = "Ya existe un termino ignorado con esa combinacion."
            raise ValueError(msg) from exc

        self._session.refresh(model)
        return self._to_entity(model)

    def update(self, term_id: int, term: str, scope: str, language: str) -> IgnoredTerm:
        model = self._session.get(IgnoredTermModel, term_id)
        if model is None:
            msg = "El termino ignorado seleccionado no existe."
            raise ValueError(msg)

        model.term = term
        model.scope = scope
        model.language = language
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            msg = "Ya existe un termino ignorado con esa combinacion."
            raise ValueError(msg) from exc

        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, term_id: int) -> None:
        model = self._session.get(IgnoredTermModel, term_id)
        if model is None:
            msg = "El termino ignorado seleccionado no existe."
            raise ValueError(msg)

        self._session.delete(model)
        self._session.commit()

    def _to_entity(self, model: IgnoredTermModel) -> IgnoredTerm:
        return IgnoredTerm(
            id=model.id,
            term=model.term,
            scope=model.scope,
            language=model.language,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
