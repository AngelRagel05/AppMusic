from __future__ import annotations

from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.deleteLocalFolderInputDto import DeleteLocalFolderInputDto
from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.updateLocalFolderInputDto import UpdateLocalFolderInputDto
from app.application.use_cases import (
    ActivateLocalFolderUseCase,
    DefineMainLocalFolderUseCase,
    DeleteLocalFolderUseCase,
    GetActiveLocalFolderUseCase,
    ListLocalFoldersUseCase,
    UpdateLocalFolderUseCase,
)


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
        self._folders_cache: list[LocalFolderDto] = []
        self._folders_by_id: dict[int, LocalFolderDto] = {}
        self._active_folder_cache: LocalFolderDto | None = None

    def refreshState(self) -> tuple[list[LocalFolderDto], LocalFolderDto | None]:
        folders = self._list_use_case.execute()
        activeFolder = self._get_active_use_case.execute()
        self._storeFolders(folders)
        self._active_folder_cache = activeFolder
        return folders, activeFolder

    def load_folders(self) -> list[LocalFolderDto]:
        if not self._folders_cache:
            self.refreshState()
        return list(self._folders_cache)

    def load_active_folder(self) -> LocalFolderDto | None:
        if self._active_folder_cache is None and not self._folders_cache:
            self.refreshState()
        return self._active_folder_cache

    def find_folder_by_id(self, local_folder_id: int) -> LocalFolderDto | None:
        if not self._folders_cache:
            self.refreshState()
        return self._folders_by_id.get(local_folder_id)

    def activate_folder(self, local_folder_id: int) -> LocalFolderDto:
        localFolder = self._activate_use_case.execute(
            ActivateLocalFolderInputDto(local_folder_id=local_folder_id)
        )
        self.refreshState()
        return localFolder

    def define_main_folder(self, path: str) -> LocalFolderDto:
        localFolder = self._define_main_use_case.execute(
            DefineMainLocalFolderInputDto(path=path)
        )
        self.refreshState()
        return localFolder

    def update_folder(self, local_folder_id: int, path: str) -> LocalFolderDto:
        localFolder = self._update_use_case.execute(
            UpdateLocalFolderInputDto(local_folder_id=local_folder_id, path=path)
        )
        self.refreshState()
        return localFolder

    def delete_folder(self, local_folder_id: int) -> None:
        self._delete_use_case.execute(
            DeleteLocalFolderInputDto(local_folder_id=local_folder_id)
        )
        self.refreshState()

    def _storeFolders(self, folders: list[LocalFolderDto]) -> None:
        self._folders_cache = list(folders)
        self._folders_by_id = {folder.id: folder for folder in folders}
