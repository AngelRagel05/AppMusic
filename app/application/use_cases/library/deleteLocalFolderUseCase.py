from __future__ import annotations

from app.application.dto.deleteLocalFolderInputDto import DeleteLocalFolderInputDto
from app.application.validators.library.localFolderValidators import (
    validateLocalFolderId,
)
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository


class DeleteLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DeleteLocalFolderInputDto) -> None:
        validateLocalFolderId(input_dto.local_folder_id)
        self._repository.delete(input_dto.local_folder_id)
