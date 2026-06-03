from __future__ import annotations

from os import walk
from pathlib import Path

from loguru import logger


class LocalMusicScanner:
    def scanMp3Files(self, folderPath: str) -> list[str]:
        rootPath = Path(folderPath).expanduser().resolve()
        if not rootPath.exists() or not rootPath.is_dir():
            return []

        discoveredFilePaths: list[str] = []

        def handleWalkError(error: OSError) -> None:
            logger.warning("No se pudo acceder a la ruta durante el escaneo: {}", error.filename or folderPath)

        for currentRoot, _, fileNames in walk(rootPath, onerror=handleWalkError):
            currentRootPath = Path(currentRoot)
            for fileName in fileNames:
                if not fileName.lower().endswith(".mp3"):
                    continue

                try:
                    absoluteFilePath = (currentRootPath / fileName).resolve()
                except OSError:
                    logger.warning("No se pudo resolver el archivo detectado durante el escaneo: {}", fileName)
                    continue

                discoveredFilePaths.append(str(absoluteFilePath))

        return sorted(set(discoveredFilePaths), key=str.casefold)
