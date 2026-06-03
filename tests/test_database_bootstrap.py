from __future__ import annotations

from app.infrastructure.persistence.database.bootstrap import (
    DEFAULT_IGNORED_TERMS,
    DatabaseBootstrapper,
)
from app.infrastructure.persistence.database.models import IgnoredTerm
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker


def create_bootstrapper() -> tuple[DatabaseBootstrapper, sessionmaker[Session]]:
    engine = create_engine("sqlite:///:memory:", future=True)
    session_factory = sessionmaker(bind=engine, class_=Session)
    return DatabaseBootstrapper(engine, session_factory), session_factory


def test_bootstrap_creates_tables_and_seeds_default_ignored_terms() -> None:
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
