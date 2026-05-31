from __future__ import annotations

from pathlib import Path

import pytest

from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.use_cases.activateLocalFolderUseCase import (
    ActivateLocalFolderUseCase,
)
from app.application.use_cases.defineMainLocalFolderUseCase import (
    DefineMainLocalFolderUseCase,
)
from app.application.use_cases.getActiveLocalFolderUseCase import (
    GetActiveLocalFolderUseCase,
)
from app.application.use_cases.listLocalFoldersUseCase import ListLocalFoldersUseCase
from app.domain.entities.localFolder import LocalFolder
from app.domain.services.localFolderRepository import LocalFolderRepository


class InMemoryLocalFolderRepository(LocalFolderRepository):
    def __init__(self) -> None:
        self._folders: list[LocalFolder] = []
        self._next_id = 1

    def get_active(self) -> LocalFolder | None:
        for folder in self._folders:
            if folder.is_active:
                return folder
        return None

    def list_all(self) -> list[LocalFolder]:
        return list(self._folders)

    def save_as_active(self, path: str, display_name: str) -> LocalFolder:
        self._folders = [
            LocalFolder(
                id=folder.id,
                path=folder.path,
                display_name=folder.display_name,
                is_active=False,
                created_at=folder.created_at,
                updated_at=folder.updated_at,
            )
            for folder in self._folders
        ]

        for index, folder in enumerate(self._folders):
            if folder.path != path:
                continue

            updated_folder = LocalFolder(
                id=folder.id,
                path=path,
                display_name=display_name,
                is_active=True,
                created_at=folder.created_at,
                updated_at=folder.updated_at,
            )
            self._folders[index] = updated_folder
            return updated_folder

        local_folder = LocalFolder(
            id=self._next_id,
            path=path,
            display_name=display_name,
            is_active=True,
        )
        self._folders.append(local_folder)
        self._next_id += 1
        return local_folder

    def activate(self, local_folder_id: int) -> LocalFolder:
        self._folders = [
            LocalFolder(
                id=folder.id,
                path=folder.path,
                display_name=folder.display_name,
                is_active=False,
                created_at=folder.created_at,
                updated_at=folder.updated_at,
            )
            for folder in self._folders
        ]

        for index, folder in enumerate(self._folders):
            if folder.id != local_folder_id:
                continue

            updated_folder = LocalFolder(
                id=folder.id,
                path=folder.path,
                display_name=folder.display_name,
                is_active=True,
                created_at=folder.created_at,
                updated_at=folder.updated_at,
            )
            self._folders[index] = updated_folder
            return updated_folder

        msg = "La biblioteca seleccionada no existe."
        raise ValueError(msg)


def test_define_main_local_folder_use_case_persists_existing_folder_as_active(
    tmp_path: Path,
) -> None:
    repository = InMemoryLocalFolderRepository()
    use_case = DefineMainLocalFolderUseCase(repository)

    local_folder = use_case.execute(
        DefineMainLocalFolderInputDto(path=f"  {tmp_path}  ")
    )

    assert local_folder.path == str(tmp_path.resolve())
    assert local_folder.display_name == tmp_path.name
    assert local_folder.is_active is True


def test_define_main_local_folder_use_case_rejects_missing_folder(tmp_path: Path) -> None:
    repository = InMemoryLocalFolderRepository()
    use_case = DefineMainLocalFolderUseCase(repository)
    missing_folder = tmp_path / "missing"

    with pytest.raises(ValueError, match="no existe"):
        use_case.execute(DefineMainLocalFolderInputDto(path=str(missing_folder)))


def test_get_active_local_folder_use_case_returns_none_when_no_folder_is_active() -> None:
    repository = InMemoryLocalFolderRepository()
    use_case = GetActiveLocalFolderUseCase(repository)

    assert use_case.execute() is None


def test_list_local_folders_use_case_returns_saved_libraries(tmp_path: Path) -> None:
    repository = InMemoryLocalFolderRepository()
    define_use_case = DefineMainLocalFolderUseCase(repository)
    list_use_case = ListLocalFoldersUseCase(repository)
    first_folder = tmp_path / "first"
    second_folder = tmp_path / "second"
    first_folder.mkdir()
    second_folder.mkdir()

    define_use_case.execute(DefineMainLocalFolderInputDto(path=str(first_folder)))
    define_use_case.execute(DefineMainLocalFolderInputDto(path=str(second_folder)))

    local_folders = list_use_case.execute()

    assert len(local_folders) == 2
    assert {local_folder.display_name for local_folder in local_folders} == {"first", "second"}


def test_define_main_local_folder_use_case_deactivates_previous_folder(tmp_path: Path) -> None:
    repository = InMemoryLocalFolderRepository()
    use_case = DefineMainLocalFolderUseCase(repository)
    first_folder = tmp_path / "first"
    second_folder = tmp_path / "second"
    first_folder.mkdir()
    second_folder.mkdir()

    use_case.execute(DefineMainLocalFolderInputDto(path=str(first_folder)))
    use_case.execute(DefineMainLocalFolderInputDto(path=str(second_folder)))

    active_folder = repository.get_active()

    assert active_folder is not None
    assert active_folder.path == str(second_folder.resolve())


def test_activate_local_folder_use_case_switches_active_library(tmp_path: Path) -> None:
    repository = InMemoryLocalFolderRepository()
    define_use_case = DefineMainLocalFolderUseCase(repository)
    activate_use_case = ActivateLocalFolderUseCase(repository)
    first_folder = tmp_path / "first"
    second_folder = tmp_path / "second"
    first_folder.mkdir()
    second_folder.mkdir()

    first_local_folder = define_use_case.execute(
        DefineMainLocalFolderInputDto(path=str(first_folder))
    )
    define_use_case.execute(DefineMainLocalFolderInputDto(path=str(second_folder)))

    activated_folder = activate_use_case.execute(
        ActivateLocalFolderInputDto(local_folder_id=first_local_folder.id)
    )

    assert activated_folder.id == first_local_folder.id
    assert activated_folder.is_active is True
    active_folder = repository.get_active()
    assert active_folder is not None
    assert active_folder.id == first_local_folder.id
