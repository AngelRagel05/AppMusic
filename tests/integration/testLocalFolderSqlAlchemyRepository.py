from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.persistence import LocalFolderSqlAlchemyRepository
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import LocalFolder as LocalFolderModel


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def test_get_active_returns_none_when_there_is_no_active_folder() -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)

    assert repository.get_active() is None


def test_list_all_returns_saved_libraries(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)
    first_folder = tmp_path / "first"
    second_folder = tmp_path / "second"
    first_folder.mkdir()
    second_folder.mkdir()

    repository.save_as_active(str(first_folder), first_folder.name)
    repository.save_as_active(str(second_folder), second_folder.name)

    local_folders = repository.list_all()

    assert len(local_folders) == 2


def test_save_as_active_persists_folder_and_marks_it_active(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)

    local_folder = repository.save_as_active(str(tmp_path), tmp_path.name)

    assert local_folder.id is not None
    assert local_folder.is_active is True
    assert session.query(LocalFolderModel).count() == 1


def test_save_as_active_rejects_duplicate_saved_path(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)

    repository.save_as_active(str(tmp_path), tmp_path.name)

    try:
        repository.save_as_active(str(tmp_path), "Otro nombre")
    except ValueError as exc:
        assert "ya esta guardada" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError al guardar una ruta duplicada")


def test_save_as_active_deactivates_previous_active_folder(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)
    first_folder = tmp_path / "first"
    second_folder = tmp_path / "second"
    first_folder.mkdir()
    second_folder.mkdir()

    repository.save_as_active(str(first_folder), first_folder.name)
    repository.save_as_active(str(second_folder), second_folder.name)

    active_folders = (
        session.query(LocalFolderModel)
        .filter(LocalFolderModel.is_active.is_(True))
        .all()
    )

    assert len(active_folders) == 1
    assert active_folders[0].path == str(second_folder)


def test_activate_switches_back_to_an_existing_library(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)
    first_folder = tmp_path / "first"
    second_folder = tmp_path / "second"
    first_folder.mkdir()
    second_folder.mkdir()

    first_local_folder = repository.save_as_active(str(first_folder), first_folder.name)
    repository.save_as_active(str(second_folder), second_folder.name)

    activated_folder = repository.activate(first_local_folder.id or 0)

    assert activated_folder.id == first_local_folder.id
    assert activated_folder.is_active is True
    active_folder = repository.get_active()
    assert active_folder is not None
    assert active_folder.id == first_local_folder.id


def test_update_changes_existing_library_path(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)
    first_folder = tmp_path / "first"
    renamed_folder = tmp_path / "renamed"
    first_folder.mkdir()
    renamed_folder.mkdir()

    created_folder = repository.save_as_active(str(first_folder), first_folder.name)

    updated_folder = repository.update(
        created_folder.id or 0,
        str(renamed_folder),
        "Coleccion renombrada",
    )

    assert updated_folder.path == str(renamed_folder)
    assert updated_folder.display_name == "Coleccion renombrada"


def test_delete_removes_existing_library(tmp_path: Path) -> None:
    session = create_session()
    repository = LocalFolderSqlAlchemyRepository(session)
    folder = tmp_path / "first"
    folder.mkdir()

    created_folder = repository.save_as_active(str(folder), folder.name)

    repository.delete(created_folder.id or 0)

    assert repository.list_all() == []
