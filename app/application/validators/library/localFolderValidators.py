from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NormalizedLocalFolderData:
    path: str
    display_name: str


def validateLocalFolderId(local_folder_id: int) -> None:
    if local_folder_id <= 0:
        msg = "La biblioteca seleccionada no es valida."
        raise ValueError(msg)


def normalizeLocalFolderData(path: str) -> NormalizedLocalFolderData:
    normalized_path = path.strip()
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
    return NormalizedLocalFolderData(
        path=resolved_path,
        display_name=display_name,
    )
