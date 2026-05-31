from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMainWindow

from app.presentation.styles import applyComponentQss
from app.presentation.ui.mainScreen.mainWindowPage.mainWindowPage import MainWindowPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._page = MainWindowPage()

        self.setObjectName("mainWindowRoot")
        self.setWindowTitle("AppMusic")
        self.resize(1280, 820)
        self.showMaximized()
        self.setCentralWidget(self._page)
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    @property
    def page(self) -> MainWindowPage:
        return self._page
