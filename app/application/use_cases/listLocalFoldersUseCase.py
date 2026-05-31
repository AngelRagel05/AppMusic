from __future__ import annotations

from app.application.dto.localFolderDto import LocalFolderDto
from app.domain.services.localFolderRepository import LocalFolderRepository


class ListLocalFoldersUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self) -> list[LocalFolderDto]:
        local_folders = self._repository.list_all()
        return [
            LocalFolderDto(
                id=local_folder.id or 0,
                path=local_folder.path,
                display_name=local_folder.display_name,
                is_active=local_folder.is_active,
            )
            for local_folder in local_folders
        ]
