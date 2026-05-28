from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music App")
        self.resize(900, 600)

        self._status_label = QLabel(
            "Base del proyecto lista.\n"
            "La aplicacion se ira construyendo paso a paso segun tus directrices."
        )

        layout = QVBoxLayout()
        layout.addWidget(self._status_label)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
