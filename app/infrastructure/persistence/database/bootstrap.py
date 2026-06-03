from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import IgnoredTerm

DEFAULT_IGNORED_TERMS: tuple[tuple[str, str, str], ...] = (
    ("official", "title", "global"),
    ("video", "title", "global"),
    ("audio", "title", "global"),
    ("lyrics", "title", "global"),
    ("hd", "title", "global"),
    ("remastered", "title", "global"),
)


class DatabaseBootstrapper:
    def __init__(self, engine: Engine, session_factory: sessionmaker[Session]) -> None:
        self._engine = engine
        self._session_factory = session_factory

    def bootstrap(self) -> None:
        Base.metadata.create_all(self._engine)

        with self._session_factory() as session:
            self._seed_ignored_terms(session, DEFAULT_IGNORED_TERMS)
            session.commit()

    def _seed_ignored_terms(
        self,
        session: Session,
        ignored_terms: Iterable[tuple[str, str, str]],
    ) -> None:
        for term, scope, language in ignored_terms:
            existing_term = session.scalar(
                select(IgnoredTerm).where(
                    IgnoredTerm.term == term,
                    IgnoredTerm.scope == scope,
                    IgnoredTerm.language == language,
                )
            )
            if existing_term is not None:
                continue

            session.add(
                IgnoredTerm(
                    term=term,
                    scope=scope,
                    language=language,
                    is_active=True,
                )
            )
