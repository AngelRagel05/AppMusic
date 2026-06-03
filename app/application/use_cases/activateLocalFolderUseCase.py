from __future__ import annotations

from app.application.dto.activateLocalFolderInputDto import ActivateLocalFolderInputDto
from app.application.dto.localFolderDto import LocalFolderDto
from app.domain.repositories.localFolderRepository import LocalFolderRepository


class ActivateLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: ActivateLocalFolderInputDto) -> LocalFolderDto:
        if input_dto.local_folder_id <= 0:
            msg = "La biblioteca seleccionada no es valida."
            raise ValueError(msg)

        local_folder = self._repository.activate(input_dto.local_folder_id)
        return LocalFolderDto(
            id=local_folder.id or 0,
            path=local_folder.path,
            display_name=local_folder.display_name,
            is_active=local_folder.is_active,
        )
