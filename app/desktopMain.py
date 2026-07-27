from __future__ import annotations

import sys
from pathlib import Path
from threading import Thread

import uvicorn
from alembic import command
from alembic.config import Config
from loguru import logger

from app.config.settings import PROJECT_ROOT, Settings, get_settings
from app.shared.utils import configure_logging


def resolveBundledResource(relative_path: str) -> Path:
    bundle_directory = Path(
        getattr(sys, "_MEIPASS", PROJECT_ROOT)
    ).resolve(strict=False)
    return bundle_directory / relative_path


def runPendingMigrations(settings: Settings) -> None:
    configuration_path = resolveBundledResource("alembic.ini")
    migrations_path = resolveBundledResource("migrations")
    if not configuration_path.is_file() or not migrations_path.is_dir():
        raise RuntimeError(
            "No se encontraron los recursos de Alembic incluidos con SoundShelf."
        )

    alembic_config = Config(str(configuration_path))
    alembic_config.set_main_option("script_location", str(migrations_path))
    alembic_config.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_config, "head")


def watchForShutdown(server: uvicorn.Server) -> None:
    try:
        for line in sys.stdin:
            if line.strip().lower() == "shutdown":
                logger.info("Cierre solicitado por el proceso Electron.")
                server.should_exit = True
                return
    except (OSError, ValueError):
        logger.warning("El canal de control con Electron se ha cerrado.")
    server.should_exit = True


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level, settings.logFilePath)
    logger.info("Aplicando migraciones pendientes antes de iniciar la API.")
    runPendingMigrations(settings)

    from app.api import createApi

    application = createApi(settings=settings)
    server = uvicorn.Server(
        uvicorn.Config(
            application,
            host=settings.api_host,
            port=settings.api_port,
            log_config=None,
            access_log=False,
        )
    )
    Thread(
        target=watchForShutdown,
        args=(server,),
        name="soundshelf-electron-control",
        daemon=True,
    ).start()
    logger.info(
        "FastAPI listo para iniciar en http://{}:{}.",
        settings.api_host,
        settings.api_port,
    )
    server.run()
    logger.info("FastAPI se ha detenido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
