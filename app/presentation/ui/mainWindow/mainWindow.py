from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QMainWindow,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.presentation.ui.ignoredTerms import IgnoredTermsSection
from app.presentation.ui.localLibraries import LocalLibrariesSection
from app.presentation.ui.mainWindow.heroSection import HeroSection
from app.presentation.styles import applyComponentQss
from app.presentation.viewmodels.ignored_terms_view_model import IgnoredTermsViewModel
from app.presentation.viewmodels.localFolderViewModel import LocalFolderViewModel


class MainWindow(QMainWindow):
    def __init__(
        self,
        local_folder_view_model: LocalFolderViewModel,
        ignored_terms_view_model: IgnoredTermsViewModel,
    ) -> None:
        super().__init__()
        self._local_folder_view_model = local_folder_view_model
        self._ignored_terms_view_model = ignored_terms_view_model
        self.setObjectName("mainWindowRoot")
        self.setWindowTitle("AppMusic")
        self.resize(1280, 820)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self._heroSection = HeroSection()
        self._localLibrariesSection = LocalLibrariesSection()
        self._ignoredTermsSection = IgnoredTermsSection()

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(28, 24, 28, 28)
        page_layout.setSpacing(20)
        page_layout.addWidget(self._heroSection)
        page_layout.addLayout(self._buildMainContent())
        page_layout.addStretch()

        page = QWidget()
        page.setLayout(page_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(page)

        self.setCentralWidget(scroll_area)

        self._localLibrariesSection.browseFolderButton.clicked.connect(self._handle_browse_folder)
        self._localLibrariesSection.saveFolderButton.clicked.connect(self._handle_save_folder)
        self._localLibrariesSection.activateFolderButton.clicked.connect(
            self._handle_activate_folder
        )
        self._ignoredTermsSection.createButton.clicked.connect(self._handle_create_term)

        self._load_folders()
        self._load_terms()
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    def _buildMainContent(self) -> QGridLayout:
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(20)
        layout.addWidget(self._localLibrariesSection, 0, 0)
        layout.addWidget(self._ignoredTermsSection, 0, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        return layout

    def _load_folders(self) -> None:
        local_folders = self._local_folder_view_model.load_folders()
        foldersTable = self._localLibrariesSection.foldersTable
        foldersTable.setRowCount(len(local_folders))

        for row_index, local_folder in enumerate(local_folders):
            self._set_item(row_index, 0, local_folder.display_name, foldersTable)
            self._set_item(row_index, 1, local_folder.path, foldersTable)
            self._set_item(
                row_index,
                2,
                "Si" if local_folder.is_active else "No",
                foldersTable,
            )
            name_item = foldersTable.item(row_index, 0)
            if name_item is not None:
                name_item.setData(Qt.ItemDataRole.UserRole, local_folder.id)

        self._heroSection.libraryCountValueLabel.setText(f"{len(local_folders)} bibliotecas guardadas")

        active_folder = self._local_folder_view_model.load_active_folder()
        if active_folder is None:
            self._localLibrariesSection.activeFolderLabel.setText(
                "Todavia no has elegido una biblioteca principal. Guarda una carpeta o "
                "selecciona una ya existente."
            )
            self._heroSection.activeFolderValueLabel.setText("Sin biblioteca activa")
            return

        self._localLibrariesSection.activeFolderLabel.setText(
            f"<b>{active_folder.display_name}</b><br>{active_folder.path}"
        )
        self._heroSection.activeFolderValueLabel.setText(active_folder.display_name)
        self._localLibrariesSection.folderInput.setText(active_folder.path)

    def _load_terms(self) -> None:
        ignored_terms = self._ignored_terms_view_model.load_terms()
        termsTable = self._ignoredTermsSection.termsTable
        termsTable.setRowCount(len(ignored_terms))

        for row_index, ignored_term in enumerate(ignored_terms):
            self._set_item(row_index, 0, ignored_term.term, termsTable)
            self._set_item(row_index, 1, ignored_term.scope, termsTable)
            self._set_item(row_index, 2, ignored_term.language, termsTable)
            self._set_item(
                row_index,
                3,
                "Si" if ignored_term.is_active else "No",
                termsTable,
            )

    def _handle_browse_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta principal",
            self._localLibrariesSection.folderInput.text(),
        )
        if selected_folder:
            self._localLibrariesSection.folderInput.setText(selected_folder)

    def _handle_save_folder(self) -> None:
        try:
            local_folder = self._local_folder_view_model.define_main_folder(
                self._localLibrariesSection.folderInput.text()
            )
        except ValueError as exc:
            self._heroSection.statusLabel.setText(str(exc))
            return

        self._load_folders()
        self._heroSection.statusLabel.setText(
            f'Biblioteca "{local_folder.display_name}" guardada y activada correctamente.'
        )

    def _handle_activate_folder(self) -> None:
        selected_items = self._localLibrariesSection.foldersTable.selectedItems()
        if not selected_items:
            self._heroSection.statusLabel.setText(
                "Selecciona una biblioteca guardada para activarla."
            )
            return

        selected_row = selected_items[0].row()
        folder_item = self._localLibrariesSection.foldersTable.item(selected_row, 0)
        if folder_item is None:
            self._heroSection.statusLabel.setText("No se pudo leer la biblioteca seleccionada.")
            return

        local_folder_id = folder_item.data(Qt.ItemDataRole.UserRole)
        try:
            local_folder = self._local_folder_view_model.activate_folder(int(local_folder_id))
        except (TypeError, ValueError) as exc:
            self._heroSection.statusLabel.setText(str(exc))
            return

        self._load_folders()
        self._heroSection.statusLabel.setText(
            f'Ahora estas trabajando con la biblioteca "{local_folder.display_name}".'
        )

    def _handle_create_term(self) -> None:
        try:
            created_term = self._ignored_terms_view_model.create_term(
                self._ignoredTermsSection.termInput.text(),
                self._ignoredTermsSection.scopeInput.currentText(),
                self._ignoredTermsSection.languageInput.currentText(),
            )
        except ValueError as exc:
            self._heroSection.statusLabel.setText(str(exc))
            return

        self._ignoredTermsSection.termInput.clear()
        self._load_terms()
        self._heroSection.statusLabel.setText(
            f'Termino "{created_term.term}" guardado para el scope "{created_term.scope}".'
        )

    def _set_item(
        self,
        row_index: int,
        column_index: int,
        value: str,
        table: QTableWidget,
    ) -> None:
        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(row_index, column_index, item)
