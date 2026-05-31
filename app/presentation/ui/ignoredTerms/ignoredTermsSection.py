from __future__ import annotations

from pathlib import Path

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
    QVBoxLayout,
    QWidget,
)

from app.presentation.styles import applyComponentQss
from app.presentation.ui.shared import configureDataTable

SCOPE_OPTIONS = ("title", "artist", "album")
LANGUAGE_OPTIONS = ("global", "es", "en")


class IgnoredTermsSection(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ignoredTermsRoot")

        self.termsCaption = QLabel(
            "Estos terminos se ignoran al normalizar nombres de canciones y videos."
        )
        self.termsCaption.setObjectName("sectionHint")
        self.termInput = QLineEdit()
        self.termInput.setPlaceholderText("Ejemplo: live, official, remastered")
        self.scopeInput = QComboBox()
        self.scopeInput.addItems(SCOPE_OPTIONS)
        self.languageInput = QComboBox()
        self.languageInput.addItems(LANGUAGE_OPTIONS)
        self.createButton = QPushButton("Guardar termino ignorado")
        self.createButton.setObjectName("primaryButton")

        self.termsTable = QTableWidget(0, 4)
        self.termsTable.setHorizontalHeaderLabels(["Termino", "Scope", "Idioma", "Activo"])
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

    def _buildHeader(self) -> QWidget:
        container = QWidget()
        title = QLabel("Terminos ignorados")
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
        form = QGroupBox("Anadir termino")
        form.setObjectName("softGroup")
        layout = QFormLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addRow("Termino", self.termInput)
        layout.addRow("Scope", self.scopeInput)
        layout.addRow("Idioma", self.languageInput)

        actionsLayout = QHBoxLayout()
        actionsLayout.addWidget(self.createButton)
        actionsLayout.addStretch()
        layout.addRow("", actionsLayout)
        form.setLayout(layout)
        return form
