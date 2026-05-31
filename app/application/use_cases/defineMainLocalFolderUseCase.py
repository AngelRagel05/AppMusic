from __future__ import annotations

from pathlib import Path

from app.application.dto.defineMainLocalFolderInputDto import (
    DefineMainLocalFolderInputDto,
)
from app.application.dto.localFolderDto import LocalFolderDto
from app.domain.services.localFolderRepository import LocalFolderRepository


class DefineMainLocalFolderUseCase:
    def __init__(self, repository: LocalFolderRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DefineMainLocalFolderInputDto) -> LocalFolderDto:
        normalized_path = input_dto.path.strip()
        if not normalized_path:
            msg = "La carpeta principal no puede estar vacia."
            raise ValueError(msg)

        folder_path = Path(normalized_path).expanduser()
        if not folder_path.exists():
            msg = "La carpeta indicada no existe."
            raise ValueError(msg)

        if not folder_path.is_dir():
            msg = "La ruta indicada no es una carpeta."
            raise ValueError(msg)

        resolved_path = str(folder_path.resolve())
        display_name = folder_path.resolve().name or resolved_path
        local_folder = self._repository.save_as_active(
            path=resolved_path,
            display_name=display_name,
        )
        return LocalFolderDto(
            id=local_folder.id or 0,
            path=local_folder.path,
            display_name=local_folder.display_name,
            is_active=local_folder.is_active,
        )
