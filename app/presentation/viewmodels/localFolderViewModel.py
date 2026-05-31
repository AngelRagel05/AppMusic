from __future__ import annotations

from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.dto.localFolderDto import LocalFolderDto
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


class LocalFolderViewModel:
    def __init__(
        self,
        list_use_case: ListLocalFoldersUseCase,
        get_active_use_case: GetActiveLocalFolderUseCase,
        activate_use_case: ActivateLocalFolderUseCase,
        define_main_use_case: DefineMainLocalFolderUseCase,
    ) -> None:
        self._list_use_case = list_use_case
        self._get_active_use_case = get_active_use_case
        self._activate_use_case = activate_use_case
        self._define_main_use_case = define_main_use_case

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
