from __future__ import annotations

from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.use_cases.defineMainLocalFolderUseCase import (
    DefineMainLocalFolderUseCase,
)
from app.application.use_cases.getActiveLocalFolderUseCase import (
    GetActiveLocalFolderUseCase,
)


class LocalFolderViewModel:
    def __init__(
        self,
        get_active_use_case: GetActiveLocalFolderUseCase,
        define_main_use_case: DefineMainLocalFolderUseCase,
    ) -> None:
        self._get_active_use_case = get_active_use_case
        self._define_main_use_case = define_main_use_case

    def load_active_folder(self) -> LocalFolderDto | None:
        return self._get_active_use_case.execute()

    def define_main_folder(self, path: str) -> LocalFolderDto:
        return self._define_main_use_case.execute(
            DefineMainLocalFolderInputDto(path=path)
        )
