from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import createLabel, setStatusLabelTone
from app.presentation.uiTheme.themePalette import ThemeTokens


class ContextSummary(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["panel"])
        self._theme = theme

        self.currentLibraryValue = createLabel(self, "Sin biblioteca", theme=self._theme)
        self.songCountValue = createLabel(self, "Sin escanear", theme=self._theme)
        self.currentPlaylistValue = createLabel(self, "Sin playlist", theme=self._theme)
        self.syncStatusValue = createLabel(self, "Pendiente", theme=self._theme)

        self._build_metric("Biblioteca", self.currentLibraryValue).pack(fill="x", pady=(8, 10))
        self._build_metric("Canciones", self.songCountValue).pack(fill="x", pady=(0, 10))
        self._build_metric("Playlist", self.currentPlaylistValue).pack(fill="x", pady=(0, 10))
        self._build_metric("Estado", self.syncStatusValue).pack(fill="x")

    def showActiveFolderName(self, display_name: str) -> None:
        self.currentLibraryValue.configure(text=display_name)

    def showSongCount(self, value: str) -> None:
        self.songCountValue.configure(text=value)

    def showActivePlaylistTitle(self, title: str) -> None:
        self.currentPlaylistValue.configure(text=title)

    def showSyncStatus(self, status: str, state: str = "idle") -> None:
        self.syncStatusValue.configure(text=status)
        setStatusLabelTone(self.syncStatusValue, state, theme=self._theme)

    def _build_metric(self, title: str, value_label: tk.Label) -> tk.Frame:
        card = tk.Frame(self, bg=self._theme["surface"], padx=14, pady=12)
        title_label = createLabel(
            card,
            title,
            theme=self._theme,
            fg=self._theme["text_secondary"],
            font=("Segoe UI", 9, "bold"),
            bg=self._theme["surface"],
        )
        title_label.pack(anchor="w")
        value_label.configure(bg=self._theme["surface"], wraplength=150)
        value_label.pack(anchor="w", pady=(4, 0))
        return card
