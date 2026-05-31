from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.presentation.styles import applyComponentQss
from app.presentation.ui.shared import configureDataTable


class LocalLibrariesSection(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("localLibrariesRoot")

        self.activeFolderLabel = QLabel("Todavia no has elegido una biblioteca principal.")
        self.activeFolderLabel.setWordWrap(True)
        self.savedFoldersCaption = QLabel(
            "Guarda varias bibliotecas y activa la que quieras usar en este momento."
        )
        self.savedFoldersCaption.setObjectName("sectionHint")
        self.folderInput = QLineEdit()
        self.folderInput.setPlaceholderText(r"Ejemplo: D:\Musica\Biblioteca Principal")
        self.browseFolderButton = QPushButton("Explorar carpeta")
        self.browseFolderButton.setObjectName("secondaryButton")
        self.saveFolderButton = QPushButton("Guardar como biblioteca")
        self.saveFolderButton.setObjectName("primaryButton")
        self.activateFolderButton = QPushButton("Activar biblioteca seleccionada")
        self.activateFolderButton.setObjectName("secondaryButton")

        self.foldersTable = QTableWidget(0, 3)
        self.foldersTable.setHorizontalHeaderLabels(["Biblioteca", "Ruta", "Activa"])
        configureDataTable(self.foldersTable)
        self.foldersTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.foldersTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.foldersTable.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)
        layout.addWidget(self._buildHeader())
        layout.addWidget(self._buildActivePanel())
        layout.addWidget(self._buildForm())
        layout.addLayout(self._buildTableActions())
        layout.addWidget(self.foldersTable)
        self.setLayout(layout)
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    def _buildHeader(self) -> QWidget:
        container = QWidget()
        title = QLabel("Bibliotecas locales")
        title.setObjectName("sectionTitle")
        intro = QLabel(
            "Usa esta zona para registrar carpetas de musica y cambiar de biblioteca "
            "sin tener que volver a escribir la ruta cada vez."
        )
        intro.setObjectName("sectionHint")
        intro.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(intro)
        container.setLayout(layout)
        return container

    def _buildActivePanel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("infoPanel")
        title = QLabel("Biblioteca activa ahora mismo")
        title.setObjectName("panelTitle")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.activeFolderLabel)
        panel.setLayout(layout)
        return panel

    def _buildForm(self) -> QWidget:
        form = QGroupBox("Guardar una nueva biblioteca")
        form.setObjectName("softGroup")
        layout = QFormLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addRow("Ruta de la carpeta", self.folderInput)

        actionsLayout = QHBoxLayout()
        actionsLayout.setSpacing(10)
        actionsLayout.addWidget(self.browseFolderButton)
        actionsLayout.addWidget(self.saveFolderButton)
        actionsLayout.addStretch()
        layout.addRow("", actionsLayout)
        form.setLayout(layout)
        return form

    def _buildTableActions(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(self.savedFoldersCaption)
        layout.addStretch()
        layout.addWidget(self.activateFolderButton)
        return layout
