from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.shared.exceptions import ValidationError


@dataclass(frozen=True)
class NormalizedLocalFolderData:
    path: str
    display_name: str


def validateLocalFolderId(local_folder_id: int) -> None:
    if local_folder_id <= 0:
        msg = "La biblioteca seleccionada no es valida."
        raise ValidationError(msg)


def normalizeLocalFolderData(path: str, display_name: str = "") -> NormalizedLocalFolderData:
    normalized_path = path.strip()
    if not normalized_path:
        msg = "La carpeta principal no puede estar vacia."
        raise ValidationError(msg)

    folder_path = Path(normalized_path).expanduser()
    if not folder_path.exists():
        msg = "La carpeta indicada no existe."
        raise ValidationError(msg)

    if not folder_path.is_dir():
        msg = "La ruta indicada no es una carpeta."
        raise ValidationError(msg)

    resolved_path = str(folder_path.resolve())
    normalized_display_name = display_name.strip() or folder_path.resolve().name or resolved_path
    return NormalizedLocalFolderData(
        path=resolved_path,
        display_name=normalized_display_name,
    )
