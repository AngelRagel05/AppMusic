from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
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
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.dto.localFolderDto import LocalFolderDto
from app.presentation.styles import applyComponentQss
from app.presentation.ui.shared.dataTable import configureDataTable


class LocalLibrariesSection(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("localLibrariesRoot")

        self.activeFolderLabel = QLabel("Todavía no has elegido una biblioteca principal.")
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

    def showFolders(self, localFolders: list[LocalFolderDto]) -> None:
        self.foldersTable.setRowCount(len(localFolders))

        for rowIndex, localFolder in enumerate(localFolders):
            self._setTableItem(rowIndex, 0, localFolder.display_name)
            self._setTableItem(rowIndex, 1, localFolder.path)
            self._setTableItem(rowIndex, 2, "Si" if localFolder.is_active else "No")
            nameItem = self.foldersTable.item(rowIndex, 0)
            if nameItem is not None:
                nameItem.setData(Qt.ItemDataRole.UserRole, localFolder.id)

    def showActiveFolder(self, activeFolder: LocalFolderDto | None) -> None:
        if activeFolder is None:
            self.activeFolderLabel.setText(
                "Todavía no has elegido una biblioteca principal. Guarda una carpeta o "
                "selecciona una ya existente."
            )
            return

        self.activeFolderLabel.setText(
            f"<b>{activeFolder.display_name}</b><br>{activeFolder.path}"
        )
        self.folderInput.setText(activeFolder.path)

    def folderPath(self) -> str:
        return self.folderInput.text()

    def setFolderPath(self, path: str) -> None:
        self.folderInput.setText(path)

    def selectedFolderId(self) -> int | None:
        selectedItems = self.foldersTable.selectedItems()
        if not selectedItems:
            return None

        selectedRow = selectedItems[0].row()
        folderItem = self.foldersTable.item(selectedRow, 0)
        if folderItem is None:
            return None

        folderId = folderItem.data(Qt.ItemDataRole.UserRole)
        if folderId is None:
            return None

        return int(folderId)

    def _buildHeader(self) -> QWidget:
        container = QWidget()
        title = QLabel("Bibliotecas locales")
        title.setObjectName("sectionTitle")
        intro = QLabel(
            "Usa esta zona para registrar carpetas de música y cambiar de biblioteca "
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

    def _setTableItem(self, rowIndex: int, columnIndex: int, value: str) -> None:
        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.foldersTable.setItem(rowIndex, columnIndex, item)
