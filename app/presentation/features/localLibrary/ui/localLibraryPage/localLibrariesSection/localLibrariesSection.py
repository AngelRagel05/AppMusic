from __future__ import annotations

import customtkinter as ctk

from app.application.dto.localFolderDto import LocalFolderDto
from app.presentation.shared.widgets.statusBadge.statusBadge import StatusBadge
from app.presentation.shared.theme import (
    ActionButton,
    Signal,
    bindRecursive,
    clearChildren,
    createEntry,
    createFrame,
    createLabel,
    createScrollableFrame,
    setStatusLabelTone,
)


class _LocalFolderRow(ctk.CTkFrame):
    def __init__(self, parent, local_folder: LocalFolderDto, theme) -> None:
        self._theme = theme
        super().__init__(
            parent,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_lg"]),
            border_width=1,
            border_color=self._theme["border"],
        )
        self.activated = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._local_folder_id = local_folder.id

        self.grid_columnconfigure(0, weight=1)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        content.grid_columnconfigure(0, weight=1)

        createLabel(
            content,
            local_folder.display_name,
            theme=self._theme,
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")
        createLabel(
            content,
            local_folder.path,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=620,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        badgeTone = "success" if local_folder.is_active else "idle"
        badgeText = "Activa" if local_folder.is_active else "Guardada"
        self._statusBadge = StatusBadge(content, badgeText, badgeTone, self._theme)
        self._statusBadge.grid(row=0, column=1, sticky="e", padx=(16, 0))

        actions = createFrame(self, theme=self._theme, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))

        activateButton = ActionButton(
            actions,
            "Activar",
            variant="ghost",
            theme=self._theme,
        )
        activateButton.clicked.connect(lambda: self.activated.emit(self._local_folder_id))
        activateButton.widget.pack(side="left")

        editButton = ActionButton(actions, "Editar", variant="secondary", theme=self._theme)
        editButton.clicked.connect(lambda: self.editRequested.emit(self._local_folder_id))
        editButton.widget.pack(side="left", padx=(10, 10))

        deleteButton = ActionButton(actions, "Eliminar", variant="danger", theme=self._theme)
        deleteButton.clicked.connect(lambda: self.deleteRequested.emit(self._local_folder_id))
        deleteButton.widget.pack(side="left")

        bindRecursive(self, "<Double-Button-1>", self._emit_activate)

    def _emit_activate(self, _event) -> None:
        self.activated.emit(self._local_folder_id)


class LocalLibrariesSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.activateRequested = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()

        topGrid = createFrame(self, theme=self._theme, fg_color="transparent")
        topGrid.pack(fill="x")
        topGrid.grid_columnconfigure(0, weight=1)
        topGrid.grid_columnconfigure(1, weight=1)

        self._buildStatusCard(topGrid).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._buildComposerCard(topGrid).grid(row=0, column=1, sticky="nsew")

        self.statusLabel = createLabel(
            self,
            "Selecciona una biblioteca para activarla o actualizarla.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
        )
        self.statusLabel.pack(anchor="w", pady=(18, 12))

        listHeader = createFrame(self, theme=self._theme, fg_color="transparent")
        listHeader.pack(fill="x", pady=(8, 12))
        createLabel(
            listHeader,
            "Bibliotecas guardadas",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")

        self._rowsHost = createScrollableFrame(
            self,
            theme=self._theme,
            fg_color="transparent",
        )
        self._rowsHost.pack(fill="both", expand=True)

    def showFolders(self, local_folders: list[LocalFolderDto]) -> None:
        clearChildren(self._rowsHost)
        if not local_folders:
            self._buildEmptyState(self._rowsHost).pack(fill="x")
            return

        for local_folder in local_folders:
            row = _LocalFolderRow(self._rowsHost, local_folder, self._theme)
            row.activated.connect(self.activateRequested.emit)
            row.editRequested.connect(self.editRequested.emit)
            row.deleteRequested.connect(self.deleteRequested.emit)
            row.pack(fill="x", pady=(0, 14))

    def showActiveFolder(self, active_folder: LocalFolderDto | None) -> None:
        if active_folder is None:
            self.activeFolderValue.configure(text="Sin biblioteca configurada")
            self.activeFolderMeta.configure(text="La aplicación aún no tiene una carpeta principal.")
            self.activeFolderPath.configure(text="Añade una ruta para empezar a escanear tu música.")
            self.activeFolderBadge.setStatus("Pendiente", "idle")
            return

        self.activeFolderValue.configure(text=active_folder.display_name)
        self.activeFolderMeta.configure(text="Biblioteca lista para análisis y sincronización.")
        self.activeFolderPath.configure(text=active_folder.path)
        self.activeFolderBadge.setStatus("Activa", "success")
        self.setFolderPath(active_folder.path)

    def folderPath(self) -> str:
        return self.folderInput.get()

    def setFolderPath(self, path: str) -> None:
        self.folderInput.delete(0, "end")
        self.folderInput.insert(0, path)

    def setSaveMode(self, is_editing: bool) -> None:
        if is_editing:
            self.saveFolderButton.setText("Guardar cambios")
            self.formHelper.configure(
                text="Estás editando la biblioteca seleccionada. Guarda para actualizar la ruta principal."
            )
            return

        self.saveFolderButton.setText("Guardar biblioteca")
        self.formHelper.configure(
            text="Define la carpeta principal para escaneo, comparación y mantenimiento."
        )

    def clearForm(self) -> None:
        self.folderInput.delete(0, "end")
        self.setSaveMode(False)

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.statusLabel.configure(text=message)
        setStatusLabelTone(self.statusLabel, tone, theme=self._theme)

    def focusPrimaryInput(self) -> None:
        self.folderInput.focus_set()

    def _buildStatusCard(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Biblioteca principal",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 10))

        headerRow = createFrame(card, theme=self._theme, fg_color="transparent")
        headerRow.pack(fill="x", padx=20)
        self.activeFolderValue = createLabel(
            headerRow,
            "Sin biblioteca configurada",
            theme=self._theme,
            font=("Segoe UI", 20, "bold"),
            wraplength=360,
        )
        self.activeFolderValue.pack(side="left", anchor="w")
        self.activeFolderBadge = StatusBadge(headerRow, "Pendiente", "idle", self._theme)
        self.activeFolderBadge.pack(side="right")

        self.activeFolderMeta = createLabel(
            card,
            "La aplicación aún no tiene una carpeta principal.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=380,
        )
        self.activeFolderMeta.pack(anchor="w", padx=20, pady=(12, 6))
        self.activeFolderPath = createLabel(
            card,
            "Añade una ruta para empezar a escanear tu música.",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12),
            wraplength=380,
        )
        self.activeFolderPath.pack(anchor="w", padx=20, pady=(0, 18))
        return card

    def _buildComposerCard(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Configurar biblioteca",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 10))
        self.formHelper = createLabel(
            card,
            "Define la carpeta principal para escaneo, comparación y mantenimiento.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=380,
        )
        self.formHelper.pack(anchor="w", padx=20, pady=(0, 14))

        self.folderInput = createEntry(
            card,
            theme=self._theme,
            width=420,
            placeholder_text=r"C:\Music\Rap",
        )
        self.folderInput.pack(fill="x", padx=20)

        actions = createFrame(card, theme=self._theme, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(16, 20))
        self.browseFolderButton = ActionButton(
            actions,
            "Explorar carpeta",
            variant="secondary",
            theme=self._theme,
        )
        self.browseFolderButton.widget.pack(side="left")
        self.saveFolderButton = ActionButton(
            actions,
            "Guardar biblioteca",
            theme=self._theme,
        )
        self.saveFolderButton.widget.pack(side="right")
        return card

    def _buildEmptyState(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Todavía no hay bibliotecas guardadas",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 8))
        createLabel(
            card,
            "Guarda tu primera carpeta para verla aquí como una colección lista para escaneo y sincronización.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=760,
        ).pack(anchor="w", padx=20, pady=(0, 18))
        return card
