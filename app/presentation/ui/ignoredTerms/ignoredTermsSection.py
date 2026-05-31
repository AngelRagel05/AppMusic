from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

from app.application.dto.ignored_term_dto import IgnoredTermDto
from app.presentation.styles import applyComponentQss
from app.presentation.ui.shared.dataTable import configureDataTable

SCOPE_OPTIONS = ("title", "artist", "album")
LANGUAGE_OPTIONS = ("global", "es", "en")


class IgnoredTermsSection(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ignoredTermsRoot")

        self.termsCaption = QLabel(
            "Estos términos se ignoran al normalizar nombres de canciones y videos."
        )
        self.termsCaption.setObjectName("sectionHint")
        self.termInput = QLineEdit()
        self.termInput.setPlaceholderText("Ejemplo: live, official, remastered")
        self.scopeInput = QComboBox()
        self.scopeInput.addItems(SCOPE_OPTIONS)
        self.languageInput = QComboBox()
        self.languageInput.addItems(LANGUAGE_OPTIONS)
        self.createButton = QPushButton("Guardar término ignorado")
        self.createButton.setObjectName("primaryButton")

        self.termsTable = QTableWidget(0, 4)
        self.termsTable.setHorizontalHeaderLabels(["Término", "Scope", "Idioma", "Activo"])
        configureDataTable(self.termsTable)
        self.termsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.termsTable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.termsTable.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.termsTable.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)
        layout.addWidget(self._buildHeader())
        layout.addWidget(self._buildForm())
        layout.addWidget(self.termsCaption)
        layout.addWidget(self.termsTable)
        self.setLayout(layout)
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    def showTerms(self, ignoredTerms: list[IgnoredTermDto]) -> None:
        self.termsTable.setRowCount(len(ignoredTerms))

        for rowIndex, ignoredTerm in enumerate(ignoredTerms):
            self._setTableItem(rowIndex, 0, ignoredTerm.term)
            self._setTableItem(rowIndex, 1, ignoredTerm.scope)
            self._setTableItem(rowIndex, 2, ignoredTerm.language)
            self._setTableItem(rowIndex, 3, "Si" if ignoredTerm.is_active else "No")

    def termText(self) -> str:
        return self.termInput.text()

    def termScope(self) -> str:
        return self.scopeInput.currentText()

    def termLanguage(self) -> str:
        return self.languageInput.currentText()

    def clearTermInput(self) -> None:
        self.termInput.clear()

    def _buildHeader(self) -> QWidget:
        container = QWidget()
        title = QLabel("Términos ignorados")
        title.setObjectName("sectionTitle")
        intro = QLabel(
            "Configura palabras frecuentes como 'official' o 'live' para que la app "
            "limpie mejor los nombres antes de comparar canciones."
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

    def _buildForm(self) -> QWidget:
        form = QGroupBox("Añadir término ignorado")
        form.setObjectName("softGroup")
        layout = QFormLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addRow("Término", self.termInput)
        layout.addRow("Scope", self.scopeInput)
        layout.addRow("Idioma", self.languageInput)

        actionsLayout = QHBoxLayout()
        actionsLayout.addWidget(self.createButton)
        actionsLayout.addStretch()
        layout.addRow("", actionsLayout)
        form.setLayout(layout)
        return form

    def _setTableItem(self, rowIndex: int, columnIndex: int, value: str) -> None:
        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.termsTable.setItem(rowIndex, columnIndex, item)
