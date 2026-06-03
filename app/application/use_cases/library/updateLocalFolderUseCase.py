from __future__ import annotations

from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.updateLocalFolderInputDto import UpdateLocalFolderInputDto
from app.application.validators.library.localFolderValidators import (
    normalizeLocalFolderData,
    validateLocalFolderId,
)
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository


class UpdateLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: UpdateLocalFolderInputDto) -> LocalFolderDto:
        validateLocalFolderId(input_dto.local_folder_id)
        normalized_data = normalizeLocalFolderData(
            input_dto.path,
            input_dto.display_name,
        )
        local_folder = self._repository.update(
            input_dto.local_folder_id,
            normalized_data.path,
            normalized_data.display_name,
        )
        return LocalFolderDto(
            id=local_folder.id or 0,
            path=local_folder.path,
            display_name=local_folder.display_name,
            is_active=local_folder.is_active,
        )
