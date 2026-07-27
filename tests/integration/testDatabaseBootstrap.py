from __future__ import annotations

import pytest
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.bootstrap import (
    DEFAULT_IGNORED_TERMS,
    DatabaseBootstrapper,
)
from app.infrastructure.persistence.database.models import IgnoredTerm
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker


def create_bootstrapper(
    *,
    with_schema: bool = True,
) -> tuple[DatabaseBootstrapper, sessionmaker[Session]]:
    engine = create_engine("sqlite:///:memory:", future=True)
    if with_schema:
        Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, class_=Session)
    return DatabaseBootstrapper(engine, session_factory), session_factory


def test_bootstrap_verifies_tables_and_seeds_default_ignored_terms() -> None:
    bootstrapper, session_factory = create_bootstrapper()

    bootstrapper.bootstrap()

    inspector = inspect(session_factory.kw["bind"])
    assert "ignored_term" in inspector.get_table_names()

    with session_factory() as session:
        persisted_terms = session.scalars(select(IgnoredTerm)).all()

    assert len(persisted_terms) == len(DEFAULT_IGNORED_TERMS)


def test_bootstrap_is_idempotent_for_default_ignored_terms() -> None:
    bootstrapper, session_factory = create_bootstrapper()

    bootstrapper.bootstrap()
    bootstrapper.bootstrap()

    with session_factory() as session:
        persisted_terms = session.scalars(select(IgnoredTerm)).all()

    assert len(persisted_terms) == len(DEFAULT_IGNORED_TERMS)


def test_bootstrap_rejects_database_without_alembic_schema() -> None:
    bootstrapper, session_factory = create_bootstrapper(with_schema=False)
    engine = session_factory.kw["bind"]

    with pytest.raises(RuntimeError, match="npm run migrate"):
        bootstrapper.bootstrap()

    assert inspect(engine).get_table_names() == []
