from __future__ import annotations

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import LocalFolder
from app.infrastructure.repositories import SqlAlchemyRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def test_add_persists_entity_and_assigns_id() -> None:
    session = create_session()
    repository = SqlAlchemyRepository(session, LocalFolder)
    folder = LocalFolder(path="/music", display_name="Music", is_active=True)

    saved_folder = repository.add(folder)

    assert saved_folder.id is not None
    assert session.get(LocalFolder, saved_folder.id) is saved_folder


def test_get_by_id_returns_none_when_entity_does_not_exist() -> None:
    session = create_session()
    repository = SqlAlchemyRepository(session, LocalFolder)

    folder = repository.get_by_id(999)

    assert folder is None


def test_list_all_returns_all_persisted_entities() -> None:
    session = create_session()
    repository = SqlAlchemyRepository(session, LocalFolder)
    repository.add(LocalFolder(path="/music/a", display_name="A", is_active=False))
    repository.add(LocalFolder(path="/music/b", display_name="B", is_active=True))

    folders = repository.list_all()

    assert len(folders) == 2
    assert {folder.path for folder in folders} == {"/music/a", "/music/b"}


def test_remove_deletes_entity_from_session() -> None:
    session = create_session()
    repository = SqlAlchemyRepository(session, LocalFolder)
    folder = repository.add(LocalFolder(path="/music", display_name="Music", is_active=False))

    repository.remove(folder)

    assert repository.get_by_id(folder.id) is None
