from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def configure_logging(level: str, log_file: Path | None = None) -> None:
    logger.remove()
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | "
        "{name}:{function}:{line} | {message}"
    )
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=log_format,
    )
    if log_file is None:
        return

    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_file,
        level=level.upper(),
        format=log_format,
        encoding="utf-8",
        rotation="5 MB",
        retention=3,
    )
