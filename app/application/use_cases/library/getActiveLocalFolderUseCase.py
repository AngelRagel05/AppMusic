from __future__ import annotations

from app.application.dto.localFolderDto import LocalFolderDto
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository


class GetActiveLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self) -> LocalFolderDto | None:
        local_folder = self._repository.get_active()
        if local_folder is None:
            return None

        return LocalFolderDto(
            id=local_folder.id or 0,
            path=local_folder.path,
            display_name=local_folder.display_name,
            is_active=local_folder.is_active,
        )
