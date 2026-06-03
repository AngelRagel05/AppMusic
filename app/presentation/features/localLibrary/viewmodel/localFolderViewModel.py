from __future__ import annotations

from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.deleteLocalFolderInputDto import DeleteLocalFolderInputDto
from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.updateLocalFolderInputDto import UpdateLocalFolderInputDto
from app.application.use_cases.activateLocalFolderUseCase import (
    ActivateLocalFolderUseCase,
)
from app.application.use_cases.deleteLocalFolderUseCase import DeleteLocalFolderUseCase
from app.application.use_cases.defineMainLocalFolderUseCase import (
    DefineMainLocalFolderUseCase,
)
from app.application.use_cases.getActiveLocalFolderUseCase import (
    GetActiveLocalFolderUseCase,
)
from app.application.use_cases.listLocalFoldersUseCase import ListLocalFoldersUseCase
from app.application.use_cases.updateLocalFolderUseCase import UpdateLocalFolderUseCase


class LocalFolderViewModel:
    def __init__(
        self,
        list_use_case: ListLocalFoldersUseCase,
        get_active_use_case: GetActiveLocalFolderUseCase,
        activate_use_case: ActivateLocalFolderUseCase,
        define_main_use_case: DefineMainLocalFolderUseCase,
        update_use_case: UpdateLocalFolderUseCase,
        delete_use_case: DeleteLocalFolderUseCase,
    ) -> None:
        self._list_use_case = list_use_case
        self._get_active_use_case = get_active_use_case
        self._activate_use_case = activate_use_case
        self._define_main_use_case = define_main_use_case
        self._update_use_case = update_use_case
        self._delete_use_case = delete_use_case

    def load_folders(self) -> list[LocalFolderDto]:
        return self._list_use_case.execute()

    def load_active_folder(self) -> LocalFolderDto | None:
        return self._get_active_use_case.execute()

    def activate_folder(self, local_folder_id: int) -> LocalFolderDto:
        return self._activate_use_case.execute(
            ActivateLocalFolderInputDto(local_folder_id=local_folder_id)
        )

    def define_main_folder(self, path: str) -> LocalFolderDto:
        return self._define_main_use_case.execute(
            DefineMainLocalFolderInputDto(path=path)
        )

    def update_folder(self, local_folder_id: int, path: str) -> LocalFolderDto:
        return self._update_use_case.execute(
            UpdateLocalFolderInputDto(local_folder_id=local_folder_id, path=path)
        )

    def delete_folder(self, local_folder_id: int) -> None:
        self._delete_use_case.execute(
            DeleteLocalFolderInputDto(local_folder_id=local_folder_id)
        )
