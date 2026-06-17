from __future__ import annotations

from collections.abc import Callable
from tkinter import filedialog
from typing import Protocol

from app.presentation.viewmodels.localLibrary.localFolderViewModel import (
    LocalFolderViewModel,
)
from app.presentation.viewmodels.localLibrary.localLibraryScanViewModel import (
    LocalLibraryScanFeedback,
    LocalLibraryScanViewModel,
)
from app.presentation.features.localLibrary.ui.localLibraryPage.localLibraryPage import (
    LocalLibraryPage,
)


class LocalFolderMonitorWorkerPort(Protocol):
    def watch(
        self,
        folder_path: str | None,
        on_folder_changed: Callable[[], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        ...

    def stop(self) -> None:
        ...


class LocalLibraryController:
    def __init__(
        self,
        page: LocalLibraryPage,
        view_model: LocalFolderViewModel,
        scan_view_model: LocalLibraryScanViewModel,
        folder_monitor_worker: LocalFolderMonitorWorkerPort,
        show_page: Callable[[str, bool], None],
        on_state_changed: Callable[[], None],
        on_comparison_data_changed: Callable[[str | None], None],
        on_action_recorded: Callable[[str], None],
        on_active_folder_changed: Callable[[str], None],
        on_song_count_changed: Callable[[str], None],
    ) -> None:
        self._page = page
        self._view_model = view_model
        self._scan_view_model = scan_view_model
        self._folder_monitor_worker = folder_monitor_worker
        self._show_page = show_page
        self._on_state_changed = on_state_changed
        self._on_comparison_data_changed = on_comparison_data_changed
        self._on_action_recorded = on_action_recorded
        self._on_active_folder_changed = on_active_folder_changed
        self._on_song_count_changed = on_song_count_changed
        self._editing_folder_id: int | None = None

    def bindEvents(self) -> None:
        self._page.onPrimaryActionRequested(self._handleScanLibraryRequested)
        self._page.onBrowseFolderRequested(self._handleBrowseFolder)
        self._page.onSaveFolderRequested(self._handleSaveFolder)
        self._page.onActivateFolderRequested(self._handleActivateFolderById)
        self._page.onEditFolderRequested(self._handleEditFolderById)
        self._page.onDeleteFolderRequested(self._handleDeleteFolderById)

    def load(self) -> None:
        local_folders, active_folder = self._view_model.refreshState()
        self._page.showFolders(local_folders)
        self._page.showActiveFolder(active_folder)
        active_folder_name = (
            active_folder.display_name if active_folder is not None else "Sin biblioteca"
        )
        self._on_active_folder_changed(active_folder_name)
        self._on_song_count_changed("Sin escanear")
        self._syncAutoRefreshMonitor(active_folder)
        self._on_state_changed()

    def activeFolder(self):
        return self._view_model.load_active_folder()

    def requestScan(self) -> None:
        self._handleScanLibraryRequested()

    def shutdown(self) -> None:
        self._folder_monitor_worker.stop()

    def _handleBrowseFolder(self) -> None:
        selected_folder = filedialog.askdirectory(
            parent=self._page.winfo_toplevel(),
            title="Seleccionar carpeta principal",
            initialdir=self._page.folderPath() or None,
        )
        if selected_folder:
            self._page.setFolderPath(selected_folder)

    def _handleSaveFolder(self) -> None:
        try:
            if self._editing_folder_id is None:
                local_folder = self._view_model.define_main_folder(
                    self._page.folderPath(),
                    self._page.folderDisplayName(),
                )
                message = (
                    f'Biblioteca "{local_folder.display_name}" guardada y activada correctamente.'
                )
            else:
                local_folder = self._view_model.update_folder(
                    self._editing_folder_id,
                    self._page.folderPath(),
                    self._page.folderDisplayName(),
                )
                message = f'Biblioteca "{local_folder.display_name}" actualizada correctamente.'
        except ValueError as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        self._editing_folder_id = None
        self._page.clearForm()
        self._renderState()
        self._on_comparison_data_changed(
            "La biblioteca local activa ha cambiado."
        )
        self._page.showStatusMessage(message, tone="success")
        self._on_action_recorded(message)

    def _handleActivateFolderById(self, selected_folder_id: int) -> None:
        selected_folder = self._view_model.find_folder_by_id(selected_folder_id)
        if selected_folder is None:
            self._page.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        if selected_folder.is_active:
            self._page.showStatusMessage(
                f'La biblioteca "{selected_folder.display_name}" ya esta activa.',
                tone="info",
            )
            return

        try:
            local_folder = self._view_model.activate_folder(selected_folder_id)
        except (TypeError, ValueError) as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        self._renderState()
        self._on_comparison_data_changed(
            "La biblioteca local activa ha cambiado."
        )
        self._page.showStatusMessage(
            f'Ahora estas trabajando con la biblioteca "{local_folder.display_name}".',
            tone="success",
        )
        self._on_action_recorded(
            f'Biblioteca activa cambiada a "{local_folder.display_name}".'
        )

    def _handleEditFolderById(self, local_folder_id: int) -> None:
        selected_folder = self._view_model.find_folder_by_id(local_folder_id)
        if selected_folder is None:
            self._page.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        self._editing_folder_id = selected_folder.id
        self._page.setFolderPath(selected_folder.path)
        self._page.setFolderDisplayName(selected_folder.display_name)
        self._page.setSaveMode(True)
        self._show_page("localLibrary", True)
        self._page.showStatusMessage(
            f'Editando la biblioteca "{selected_folder.display_name}".',
            tone="info",
        )

    def _handleDeleteFolderById(self, local_folder_id: int) -> None:
        selected_folder = self._view_model.find_folder_by_id(local_folder_id)
        if selected_folder is None:
            self._page.showStatusMessage(
                "La biblioteca seleccionada no existe.",
                tone="error",
            )
            return

        try:
            self._view_model.delete_folder(selected_folder.id)
        except ValueError as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_folder_id == selected_folder.id:
            self._editing_folder_id = None
            self._page.clearForm()
        self._renderState()
        self._on_comparison_data_changed(
            "La biblioteca local activa ha cambiado."
        )
        self._page.showStatusMessage(
            f'Biblioteca "{selected_folder.display_name}" eliminada correctamente.',
            tone="success",
        )
        self._on_action_recorded(
            f'Biblioteca "{selected_folder.display_name}" eliminada.'
        )

    def _handleScanLibraryRequested(self) -> None:
        self._scan_view_model.requestScan(
            active_folder=self._view_model.load_active_folder(),
            schedule_on_main_thread=lambda callback: self._page.after(0, callback),
            on_feedback=self._renderScanFeedback,
        )

    def _renderState(self) -> None:
        localFolders = self._view_model.load_folders()
        activeFolder = self._view_model.load_active_folder()
        self._page.showFolders(localFolders)
        self._page.showActiveFolder(activeFolder)
        activeFolderName = (
            activeFolder.display_name if activeFolder is not None else "Sin biblioteca"
        )
        self._on_active_folder_changed(activeFolderName)
        self._on_song_count_changed("Sin escanear")
        self._syncAutoRefreshMonitor(activeFolder)
        self._on_state_changed()

    def _renderScanFeedback(self, feedback: LocalLibraryScanFeedback) -> None:
        if feedback.song_count_label is not None:
            self._on_song_count_changed(feedback.song_count_label)
        self._page.showStatusMessage(feedback.status_message, tone=feedback.status_tone)
        if feedback.status_tone == "success":
            self._on_comparison_data_changed(
                "El ultimo escaneo local ha cambiado la biblioteca comparada."
            )
        if feedback.last_action_message is not None:
            self._on_action_recorded(feedback.last_action_message)

    def _syncAutoRefreshMonitor(self, activeFolder) -> None:
        folderPath = activeFolder.path if activeFolder is not None else None
        self._folder_monitor_worker.watch(
            folder_path=folderPath,
            on_folder_changed=self._handleAutoRefreshRequested,
            on_failed=self._handleAutoRefreshFailed,
        )

    def _handleAutoRefreshRequested(self) -> None:
        self._scan_view_model.requestScan(
            active_folder=self._view_model.load_active_folder(),
            schedule_on_main_thread=lambda callback: self._page.after(0, callback),
            on_feedback=self._renderScanFeedback,
            automatic=True,
        )

    def _handleAutoRefreshFailed(self, error: Exception) -> None:
        self._page.showStatusMessage(
            f"Fallo en la monitorizacion automatica: {error}",
            tone="error",
        )
