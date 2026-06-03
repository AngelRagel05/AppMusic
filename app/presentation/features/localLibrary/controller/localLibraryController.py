from __future__ import annotations

from collections.abc import Callable
from tkinter import filedialog

from app.presentation.features.localLibrary.viewmodel.localFolderViewModel import (
    LocalFolderViewModel,
)
from app.presentation.shell.mainWindow.mainWindow import MainWindow


class LocalLibraryController:
    def __init__(
        self,
        view: MainWindow,
        view_model: LocalFolderViewModel,
        on_state_changed: Callable[[], None],
        on_action_recorded: Callable[[str], None],
    ) -> None:
        self._view = view
        self._view_model = view_model
        self._on_state_changed = on_state_changed
        self._on_action_recorded = on_action_recorded
        self._editing_folder_id: int | None = None

    def bindEvents(self) -> None:
        section = self._view.page.localLibrariesSection
        section.browseFolderButton.clicked.connect(self._handleBrowseFolder)
        section.saveFolderButton.clicked.connect(self._handleSaveFolder)
        section.activateRequested.connect(self._handleActivateFolderById)
        section.editRequested.connect(self._handleEditFolderById)
        section.deleteRequested.connect(self._handleDeleteFolderById)

    def load(self) -> None:
        local_folders = self._view_model.load_folders()
        active_folder = self._view_model.load_active_folder()
        self._view.page.localLibrariesSection.showFolders(local_folders)
        self._view.page.localLibrariesSection.showActiveFolder(active_folder)
        active_folder_name = (
            active_folder.display_name if active_folder is not None else "Sin biblioteca"
        )
        self._view.page.setActiveFolderName(active_folder_name)
        self._view.page.setSongCount("Sin escanear")
        self._on_state_changed()

    def activeFolder(self):
        return self._view_model.load_active_folder()

    def _handleBrowseFolder(self) -> None:
        selected_folder = filedialog.askdirectory(
            parent=self._view.window,
            title="Seleccionar carpeta principal",
            initialdir=self._view.page.localLibrariesSection.folderPath() or None,
        )
        if selected_folder:
            self._view.page.localLibrariesSection.setFolderPath(selected_folder)

    def _handleSaveFolder(self) -> None:
        try:
            if self._editing_folder_id is None:
                local_folder = self._view_model.define_main_folder(
                    self._view.page.localLibrariesSection.folderPath()
                )
                message = (
                    f'Biblioteca "{local_folder.display_name}" guardada y activada correctamente.'
                )
            else:
                local_folder = self._view_model.update_folder(
                    self._editing_folder_id,
                    self._view.page.localLibrariesSection.folderPath(),
                )
                message = f'Biblioteca "{local_folder.display_name}" actualizada correctamente.'
        except ValueError as exc:
            self._view.page.localLibrariesSection.showStatusMessage(str(exc), tone="error")
            return

        self._editing_folder_id = None
        self._view.page.localLibrariesSection.clearForm()
        self.load()
        self._view.page.localLibrariesSection.showStatusMessage(message, tone="success")
        self._on_action_recorded(message)

    def _handleActivateFolderById(self, selected_folder_id: int) -> None:
        try:
            local_folder = self._view_model.activate_folder(selected_folder_id)
        except (TypeError, ValueError) as exc:
            self._view.page.localLibrariesSection.showStatusMessage(str(exc), tone="error")
            return

        self.load()
        self._view.page.localLibrariesSection.showStatusMessage(
            f'Ahora estas trabajando con la biblioteca "{local_folder.display_name}".',
            tone="success",
        )
        self._on_action_recorded(
            f'Biblioteca activa cambiada a "{local_folder.display_name}".'
        )

    def _handleEditFolderById(self, local_folder_id: int) -> None:
        selected_folder = self._selectedFolderById(local_folder_id)
        if selected_folder is None:
            self._view.page.localLibrariesSection.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        self._editing_folder_id = selected_folder.id
        self._view.page.localLibrariesSection.setFolderPath(selected_folder.path)
        self._view.page.localLibrariesSection.setSaveMode(True)
        self._view.page.showPage("localLibrary", focus_input=True)
        self._view.page.localLibrariesSection.showStatusMessage(
            f'Editando la biblioteca "{selected_folder.display_name}".',
            tone="info",
        )

    def _handleDeleteFolderById(self, local_folder_id: int) -> None:
        selected_folder = self._selectedFolderById(local_folder_id)
        if selected_folder is None:
            self._view.page.localLibrariesSection.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        try:
            self._view_model.delete_folder(selected_folder.id)
        except ValueError as exc:
            self._view.page.localLibrariesSection.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_folder_id == selected_folder.id:
            self._editing_folder_id = None
            self._view.page.localLibrariesSection.clearForm()
        self.load()
        self._view.page.localLibrariesSection.showStatusMessage(
            f'Biblioteca "{selected_folder.display_name}" eliminada correctamente.',
            tone="success",
        )
        self._on_action_recorded(
            f'Biblioteca "{selected_folder.display_name}" eliminada.'
        )

    def _selectedFolderById(self, local_folder_id: int):
        return next(
            (
                local_folder
                for local_folder in self._view_model.load_folders()
                if local_folder.id == local_folder_id
            ),
            None,
        )
