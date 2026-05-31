from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

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
        self.setWindowTitle("Music App")
        self.resize(900, 600)

        self._status_label = QLabel("Configura la carpeta principal y los terminos ignorados.")
        self._active_folder_label = QLabel("Carpeta principal actual: no definida.")
        self._folder_input = QLineEdit()
        self._browse_folder_button = QPushButton("Examinar")
        self._save_folder_button = QPushButton("Guardar carpeta")
        self._term_input = QLineEdit()
        self._scope_input = QLineEdit("title")
        self._language_input = QLineEdit("global")
        self._create_button = QPushButton("Agregar termino")
        self._terms_table = QTableWidget(0, 4)
        self._terms_table.setHorizontalHeaderLabels(["Termino", "Scope", "Idioma", "Activo"])
        self._terms_table.horizontalHeader().setStretchLastSection(True)
        self._terms_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._terms_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._terms_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        form_layout = QFormLayout()
        form_layout.addRow("Termino", self._term_input)
        form_layout.addRow("Scope", self._scope_input)
        form_layout.addRow("Idioma", self._language_input)

        form_actions_layout = QHBoxLayout()
        form_actions_layout.addWidget(self._create_button)
        form_actions_layout.addStretch()

        folder_actions_layout = QHBoxLayout()
        folder_actions_layout.addWidget(self._browse_folder_button)
        folder_actions_layout.addWidget(self._save_folder_button)
        folder_actions_layout.addStretch()

        folder_form_layout = QFormLayout()
        folder_form_layout.addRow("Ruta", self._folder_input)

        folder_group = QGroupBox("Carpeta principal de musica")
        folder_group_layout = QVBoxLayout()
        folder_group_layout.addWidget(self._active_folder_label)
        folder_group_layout.addLayout(folder_form_layout)
        folder_group_layout.addLayout(folder_actions_layout)
        folder_group.setLayout(folder_group_layout)

        form_group = QGroupBox("Nuevo termino ignorado")
        form_group_layout = QVBoxLayout()
        form_group_layout.addLayout(form_layout)
        form_group_layout.addLayout(form_actions_layout)
        form_group.setLayout(form_group_layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Primeros flujos funcionales: carpeta principal y terminos ignorados."))
        layout.addWidget(self._status_label)
        layout.addWidget(folder_group)
        layout.addWidget(form_group)
        layout.addWidget(self._terms_table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._browse_folder_button.clicked.connect(self._handle_browse_folder)
        self._save_folder_button.clicked.connect(self._handle_save_folder)
        self._create_button.clicked.connect(self._handle_create_term)
        self._load_active_folder()
        self._load_terms()

    def _load_active_folder(self) -> None:
        active_folder = self._local_folder_view_model.load_active_folder()
        if active_folder is None:
            self._active_folder_label.setText("Carpeta principal actual: no definida.")
            return

        self._active_folder_label.setText(
            f"Carpeta principal actual: {active_folder.display_name} - {active_folder.path}"
        )
        self._folder_input.setText(active_folder.path)

    def _load_terms(self) -> None:
        ignored_terms = self._ignored_terms_view_model.load_terms()
        self._terms_table.setRowCount(len(ignored_terms))

        for row_index, ignored_term in enumerate(ignored_terms):
            self._set_item(row_index, 0, ignored_term.term)
            self._set_item(row_index, 1, ignored_term.scope)
            self._set_item(row_index, 2, ignored_term.language)
            self._set_item(row_index, 3, "Si" if ignored_term.is_active else "No")

        self._status_label.setText(f"{len(ignored_terms)} terminos ignorados cargados.")

    def _handle_browse_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta principal",
            self._folder_input.text(),
        )
        if selected_folder:
            self._folder_input.setText(selected_folder)

    def _handle_save_folder(self) -> None:
        try:
            local_folder = self._local_folder_view_model.define_main_folder(
                self._folder_input.text()
            )
        except ValueError as exc:
            self._status_label.setText(str(exc))
            return

        self._load_active_folder()
        self._status_label.setText(
            f'Carpeta principal "{local_folder.display_name}" guardada correctamente.'
        )

    def _handle_create_term(self) -> None:
        try:
            created_term = self._ignored_terms_view_model.create_term(
                self._term_input.text(),
                self._scope_input.text(),
                self._language_input.text(),
            )
        except ValueError as exc:
            self._status_label.setText(str(exc))
            return

        self._term_input.clear()
        self._load_terms()
        self._status_label.setText(f'Termino "{created_term.term}" agregado correctamente.')

    def _set_item(self, row_index: int, column_index: int, value: str) -> None:
        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._terms_table.setItem(row_index, column_index, item)
