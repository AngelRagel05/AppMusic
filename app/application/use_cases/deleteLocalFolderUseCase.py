from __future__ import annotations

from app.application.dto.deleteLocalFolderInputDto import DeleteLocalFolderInputDto
from app.domain.services.localFolderRepository import LocalFolderRepository


class DeleteLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DeleteLocalFolderInputDto) -> None:
        if input_dto.local_folder_id <= 0:
            msg = "La biblioteca seleccionada no es valida."
            raise ValueError(msg)

        self._repository.delete(input_dto.local_folder_id)
