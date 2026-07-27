from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import Engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import IgnoredTerm

DEFAULT_IGNORED_TERMS: tuple[tuple[str, str, str], ...] = (
    ("official", "title", "global"),
    ("official video", "title", "global"),
    ("official audio", "title", "global"),
    ("official lyric video", "title", "global"),
    ("video", "title", "global"),
    ("audio", "title", "global"),
    ("lyrics", "title", "global"),
    ("lyric", "title", "global"),
    ("letras", "title", "global"),
    ("letra", "title", "global"),
    ("music video", "title", "global"),
    ("hd", "title", "global"),
    ("hq", "title", "global"),
    ("4k", "title", "global"),
    ("remastered", "title", "global"),
    ("visualizer", "title", "global"),
    ("visualiser", "title", "global"),
    ("audio oficial", "title", "global"),
    ("video oficial", "title", "global"),
    ("prod", "title", "global"),
    ("producido", "title", "global"),
)


class DatabaseBootstrapper:
    def __init__(self, engine: Engine, session_factory: sessionmaker[Session]) -> None:
        self._engine = engine
        self._session_factory = session_factory

    def bootstrap(self) -> None:
        self._verify_schema()

        with self._session_factory() as session:
            self._seed_ignored_terms(session, DEFAULT_IGNORED_TERMS)
            session.commit()

    def _verify_schema(self) -> None:
        inspector = inspect(self._engine)
        table_names = set(inspector.get_table_names())
        expected_tables = set(Base.metadata.tables)
        missing_tables = sorted(expected_tables - table_names)
        if missing_tables:
            missing = ", ".join(missing_tables)
            raise RuntimeError(
                "La base de datos no esta migrada. "
                f"Faltan las tablas: {missing}. Ejecuta `npm run migrate`."
            )

        expected_columns = {
            table_name: set(table.columns.keys())
            for table_name, table in Base.metadata.tables.items()
        }
        missing_columns = [
            f"{table_name}.{column_name}"
            for table_name, column_names in expected_columns.items()
            for column_name in sorted(
                column_names
                - {
                    column["name"]
                    for column in inspector.get_columns(table_name)
                }
            )
        ]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise RuntimeError(
                "La base de datos usa un esquema obsoleto. "
                f"Faltan las columnas: {missing}. Ejecuta `npm run migrate`."
            )

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
