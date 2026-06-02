from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import createLabel, getPageTheme, setStatusLabelTone
from app.presentation.ui.mainScreen.shared.pageHeader.pageHeader import PageHeader


class OverviewPage(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        self._theme = getPageTheme("overview")
        super().__init__(parent, bg=self._theme["bg"], padx=28, pady=20)
        self.header = PageHeader(self, "Resumen", self._theme)
        self.header.setActions("Nueva biblioteca", "Nueva playlist")

        self.activeLibraryValue = createLabel(self, "Sin biblioteca", theme=self._theme, font=("Segoe UI", 13, "bold"))
        self.activePlaylistValue = createLabel(self, "Sin playlist", theme=self._theme, font=("Segoe UI", 13, "bold"))
        self.syncStatusValue = createLabel(self, "Pendiente", theme=self._theme, font=("Segoe UI", 13, "bold"))
        self.songCountValue = createLabel(self, "Sin escanear", theme=self._theme, font=("Segoe UI", 13, "bold"))
        self.lastActionValue = createLabel(
            self,
            "Todavia no hay acciones registradas",
            theme=self._theme,
            font=("Segoe UI", 13, "bold"),
            wraplength=760,
        )

        self.header.pack(fill="x")
        self._build_summary().pack(fill="x", pady=(18, 0))

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)
        self.activeLibraryValue.configure(text=name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
        self.activePlaylistValue.configure(text=title)

    def setSongCount(self, value: str) -> None:
        self.songCountValue.configure(text=value)

    def setSyncStatus(self, value: str) -> None:
        self.syncStatusValue.configure(text=value)
        setStatusLabelTone(
            self.syncStatusValue,
            "ready" if value == "Listo" else "idle",
            theme=self._theme,
        )

    def setLastAction(self, value: str) -> None:
        self.lastActionValue.configure(text=value)

    def _build_summary(self) -> tk.Frame:
        wrapper = tk.Frame(self, bg=self._theme["bg"])
        for column in range(2):
            wrapper.grid_columnconfigure(column, weight=1)
        self._build_card(wrapper, "Biblioteca activa", self.activeLibraryValue).grid(
            row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 16)
        )
        self._build_card(wrapper, "Playlist activa", self.activePlaylistValue).grid(
            row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 16)
        )
        self._build_card(wrapper, "Estado de sincronizacion", self.syncStatusValue).grid(
            row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 16)
        )
        self._build_card(wrapper, "Canciones detectadas", self.songCountValue).grid(
            row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 16)
        )
        self._build_card(wrapper, "Ultima accion", self.lastActionValue).grid(
            row=2, column=0, columnspan=2, sticky="nsew"
        )
        return wrapper

    def _build_card(self, parent: tk.Misc, title: str, value_label: tk.Label) -> tk.Frame:
        card = tk.Frame(parent, bg=self._theme["surface"], padx=20, pady=18)
        title_label = createLabel(
            card,
            title,
            theme=self._theme,
            fg=self._theme["text_secondary"],
            font=("Segoe UI", 10, "bold"),
            bg=self._theme["surface"],
        )
        title_label.pack(anchor="w")
        value_label.configure(bg=self._theme["surface"])
        value_label.pack(anchor="w", pady=(8, 0))
        return card
