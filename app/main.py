from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.application.use_cases import BootstrapDatabaseUseCase
from app.config.settings import get_settings
from app.infrastructure.database import DatabaseBootstrapper, SessionLocal, engine
from app.presentation.ui.main_window import MainWindow
from app.utils.logging import configure_logging


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    BootstrapDatabaseUseCase(DatabaseBootstrapper(engine, SessionLocal)).execute()

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
