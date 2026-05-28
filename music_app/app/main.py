from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from music_app.app.config.settings import get_settings
from music_app.app.infrastructure.database.bootstrap import bootstrap_database
from music_app.app.presentation.ui.main_window import MainWindow
from music_app.app.utils.logging import configure_logging


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    bootstrap_database()

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

