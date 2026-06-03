from __future__ import annotations

from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.validators.library.localFolderValidators import (
    validateLocalFolderId,
)
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository


class ActivateLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: ActivateLocalFolderInputDto) -> LocalFolderDto:
        validateLocalFolderId(input_dto.local_folder_id)
        local_folder = self._repository.activate(input_dto.local_folder_id)
        return LocalFolderDto(
            id=local_folder.id or 0,
            path=local_folder.path,
            display_name=local_folder.display_name,
            is_active=local_folder.is_active,
        )
