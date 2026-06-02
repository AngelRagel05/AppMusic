from __future__ import annotations

import tkinter as tk

from app.application.dto.localFolderDto import LocalFolderDto
from app.presentation.uiTheme import (
    ActionButton,
    Signal,
    bindRecursive,
    clearChildren,
    createEntry,
    createLabel,
    setStatusLabelTone,
)
from app.presentation.uiTheme.themePalette import ThemeTokens


class _LocalFolderRow(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        local_folder: LocalFolderDto,
        theme: ThemeTokens,
    ) -> None:
        super().__init__(parent, bg=theme["surface"], padx=16, pady=14, cursor="hand2")
        self.activated = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._local_folder_id = local_folder.id
        self._theme = theme

        text_host = tk.Frame(self, bg=self._theme["surface"])
        text_host.pack(side="left", fill="both", expand=True)

        createLabel(
            text_host,
            local_folder.display_name,
            theme=self._theme,
            bg=self._theme["surface"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        createLabel(
            text_host,
            local_folder.path,
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_secondary"],
            wraplength=520,
        ).pack(anchor="w", pady=(4, 0))
        createLabel(
            text_host,
            "Contenido sin escanear",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        status = createLabel(
            self,
            "Activa" if local_folder.is_active else "Guardada",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["success"] if local_folder.is_active else self._theme["text_secondary"],
            font=("Segoe UI", 9, "bold"),
        )
        status.pack(side="left", padx=(12, 12), anchor="n")

        menu_button = tk.Menubutton(
            self,
            text="...",
            bg=self._theme["surface_alt"],
            fg=self._theme["text"],
            activebackground=self._theme["surface"],
            activeforeground=self._theme["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        menu = tk.Menu(
            menu_button,
            tearoff=0,
            bg=self._theme["surface_alt"],
            fg=self._theme["text"],
        )
        menu.add_command(
            label="Editar",
            command=lambda: self.editRequested.emit(self._local_folder_id),
        )
        menu.add_command(
            label="Eliminar",
            command=lambda: self.deleteRequested.emit(self._local_folder_id),
        )
        menu_button.configure(menu=menu)
        menu_button.pack(side="left", anchor="n")

        bindRecursive(self, "<Double-Button-1>", self._emit_activate)

    def _emit_activate(self, _event) -> None:
        self.activated.emit(self._local_folder_id)


class LocalLibrariesSection(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["bg"])
        self.activateRequested = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._theme = theme

        self.activeFolderValue = createLabel(
            self,
            "Sin biblioteca activa",
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        )
        self.activeFolderSongs = createLabel(
            self,
            "Canciones sin escanear",
            theme=self._theme,
            fg=self._theme["text_secondary"],
        )
        self.activeFolderSize = createLabel(
            self,
            "Tamano sin calcular",
            theme=self._theme,
            fg=self._theme["text_secondary"],
        )
        self.activeFolderPath = createLabel(
            self,
            "Ruta pendiente",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            wraplength=720,
        )

        self.folderInput = createEntry(self, theme=self._theme, width=48)
        self.browseFolderButton = ActionButton(
            self,
            "Explorar carpeta",
            variant="secondary",
            theme=self._theme,
        )
        self.saveFolderButton = ActionButton(self, "Guardar cambios", theme=self._theme)
        self.saveModeLabel = createLabel(
            self,
            "Crea o actualiza tu biblioteca principal desde aqui.",
            theme=self._theme,
            fg=self._theme["text_secondary"],
        )
        self.statusLabel = createLabel(
            self,
            "Doble clic en una biblioteca para activarla.",
            theme=self._theme,
            fg=self._theme["accent"],
            wraplength=720,
        )
        self.listCaption = createLabel(
            self,
            "Bibliotecas guardadas",
            theme=self._theme,
            font=("Segoe UI", 11, "bold"),
        )

        self._rowsHost = tk.Frame(self, bg=self._theme["bg"])

        self._buildComposerCard().pack(fill="x")
        self.saveModeLabel.pack(anchor="w", pady=(16, 4))
        self.statusLabel.pack(anchor="w")
        self.listCaption.pack(anchor="w", pady=(16, 8))
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
            row.pack(fill="x", pady=(0, 12))

    def showActiveFolder(self, active_folder: LocalFolderDto | None) -> None:
        if active_folder is None:
            self.activeFolderValue.configure(text="Sin biblioteca activa")
            self.activeFolderSongs.configure(text="Canciones sin escanear")
            self.activeFolderSize.configure(text="Tamano sin calcular")
            self.activeFolderPath.configure(text="Ruta pendiente")
            return

        self.activeFolderValue.configure(text=active_folder.display_name)
        self.activeFolderSongs.configure(text="Biblioteca preparada para escaneo")
        self.activeFolderSize.configure(text="Tamano sin calcular")
        self.activeFolderPath.configure(text=active_folder.path)
        self.setFolderPath(active_folder.path)

    def folderPath(self) -> str:
        return self.folderInput.get()

    def setFolderPath(self, path: str) -> None:
        self.folderInput.delete(0, tk.END)
        self.folderInput.insert(0, path)

    def setSaveMode(self, is_editing: bool) -> None:
        if is_editing:
            self.saveFolderButton.setText("Guardar cambios")
            self.saveModeLabel.configure(
                text="Estas editando la biblioteca seleccionada. Guarda para aplicar los cambios."
            )
            return

        self.saveFolderButton.setText("Guardar cambios")
        self.saveModeLabel.configure(text="Crea o actualiza tu biblioteca principal desde aqui.")

    def clearForm(self) -> None:
        self.folderInput.delete(0, tk.END)
        self.setSaveMode(False)

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.statusLabel.configure(text=message)
        setStatusLabelTone(self.statusLabel, tone, theme=self._theme)

    def focusPrimaryInput(self) -> None:
        self.folderInput.focus_set()

    def _buildComposerCard(self) -> tk.Frame:
        card = tk.Frame(self, bg=self._theme["surface"], padx=16, pady=16)
        self.activeFolderValue.configure(bg=self._theme["surface"])
        self.activeFolderSongs.configure(bg=self._theme["surface"])
        self.activeFolderSize.configure(bg=self._theme["surface"])
        self.activeFolderPath.configure(bg=self._theme["surface"])

        self.activeFolderValue.pack(in_=card, anchor="w")
        self.activeFolderSongs.pack(in_=card, anchor="w", pady=(2, 0))
        self.activeFolderPath.pack(in_=card, anchor="w", pady=(2, 0))

        controls = tk.Frame(card, bg=self._theme["surface"])
        controls.pack(fill="x", pady=(14, 0))
        self.folderInput.pack(in_=controls, side="left", fill="x", expand=True)
        self.browseFolderButton.widget.pack(in_=controls, side="left", padx=(10, 10))
        self.saveFolderButton.widget.pack(in_=controls, side="left")
        return card

    def _buildEmptyState(self, parent: tk.Misc) -> tk.Frame:
        card = tk.Frame(parent, bg=self._theme["surface"], padx=18, pady=18)
        createLabel(
            card,
            "Todavia no hay bibliotecas guardadas",
            theme=self._theme,
            bg=self._theme["surface"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        createLabel(
            card,
            "Guarda tu primera carpeta para verla aqui como una coleccion musical compacta.",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_secondary"],
            wraplength=700,
        ).pack(anchor="w", pady=(6, 0))
        return card
