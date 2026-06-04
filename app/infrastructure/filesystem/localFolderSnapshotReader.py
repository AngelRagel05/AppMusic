from __future__ import annotations

from os import walk
from pathlib import Path

from loguru import logger


class LocalFolderSnapshotReader:
    def readSnapshotSignature(self, folderPath: str) -> tuple[tuple[str, int, int], ...]:
        rootPath = Path(folderPath).expanduser().resolve()
        if not rootPath.exists() or not rootPath.is_dir():
            return ()

        snapshotEntries: list[tuple[str, int, int]] = []

        def handleWalkError(error: OSError) -> None:
            logger.warning(
                "No se pudo acceder a la ruta durante la monitorizacion: {}",
                error.filename or folderPath,
            )

        for currentRoot, _, fileNames in walk(rootPath, onerror=handleWalkError):
            currentRootPath = Path(currentRoot)
            for fileName in fileNames:
                if not fileName.lower().endswith(".mp3"):
                    continue

                try:
                    absoluteFilePath = (currentRootPath / fileName).resolve()
                    fileStats = absoluteFilePath.stat()
                except OSError:
                    logger.warning(
                        "No se pudo leer el archivo detectado durante la monitorizacion: {}",
                        fileName,
                    )
                    continue

                snapshotEntries.append(
                    (
                        str(absoluteFilePath),
                        int(fileStats.st_size),
                        int(fileStats.st_mtime_ns),
                    )
                )

        return tuple(sorted(snapshotEntries, key=lambda entry: entry[0].casefold()))
