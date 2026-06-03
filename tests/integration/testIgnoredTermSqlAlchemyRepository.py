from __future__ import annotations

import pytest
from app.infrastructure.persistence import IgnoredTermSqlAlchemyRepository
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import IgnoredTerm as IgnoredTermModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def test_list_all_returns_ignored_terms_sorted() -> None:
    session = create_session()
    session.add_all(
        [
            IgnoredTermModel(term="video", scope="title", language="global", is_active=True),
            IgnoredTermModel(term="audio", scope="title", language="global", is_active=True),
        ]
    )
    session.commit()
    repository = IgnoredTermSqlAlchemyRepository(session)

    ignored_terms = repository.list_all()

    assert [ignored_term.term for ignored_term in ignored_terms] == ["audio", "video"]


def test_create_persists_ignored_term() -> None:
    session = create_session()
    repository = IgnoredTermSqlAlchemyRepository(session)

    ignored_term = repository.create("live", "title", "global")

    assert ignored_term.id is not None
    assert session.query(IgnoredTermModel).count() == 1


def test_create_raises_error_for_duplicate_term_scope_and_language() -> None:
    session = create_session()
    repository = IgnoredTermSqlAlchemyRepository(session)
    repository.create("live", "title", "global")

    with pytest.raises(ValueError, match="Ya existe"):
        repository.create("live", "title", "global")


def test_update_modifies_persisted_ignored_term() -> None:
    session = create_session()
    repository = IgnoredTermSqlAlchemyRepository(session)
    ignored_term = repository.create("live", "title", "global")

    updated_term = repository.update(ignored_term.id or 0, "official", "artist", "en")

    assert updated_term.term == "official"
    assert updated_term.scope == "artist"
    assert updated_term.language == "en"


def test_delete_removes_persisted_ignored_term() -> None:
    session = create_session()
    repository = IgnoredTermSqlAlchemyRepository(session)
    ignored_term = repository.create("live", "title", "global")

    repository.delete(ignored_term.id or 0)

    assert session.query(IgnoredTermModel).count() == 0
