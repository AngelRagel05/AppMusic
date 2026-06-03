from __future__ import annotations

import customtkinter as ctk

from app.presentation.shared.widgets.statusBadge.statusBadge import StatusBadge
from app.presentation.uiTheme import createFrame, createLabel


class ContextSummary(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(
            parent,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_lg"]),
            border_width=1,
            border_color=self._theme["border"],
        )

        createLabel(
            self,
            "Estado del sistema",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 16))

        self._folderValue = self._build_metric("Biblioteca activa", "Sin biblioteca")
        self._playlistValue = self._build_metric("Playlist activa", "Sin playlist")
        self._songsValue = self._build_metric("Canciones detectadas", "Sin escaneo")

        statusRow = createFrame(self, theme=self._theme, fg_color="transparent")
        statusRow.pack(fill="x", padx=18, pady=(12, 18))
        createLabel(
            statusRow,
            "Sincronización",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        self._statusBadge = StatusBadge(statusRow, "Pendiente", "idle", self._theme)
        self._statusBadge.pack(side="right")

    def showActiveFolderName(self, display_name: str) -> None:
        self._folderValue.configure(text=display_name)

    def showSongCount(self, value: str) -> None:
        self._songsValue.configure(text=value)

    def showActivePlaylistTitle(self, title: str) -> None:
        self._playlistValue.configure(text=title)

    def showSyncStatus(self, status: str, state: str = "idle") -> None:
        self._statusBadge.setStatus(status, state)

    def _build_metric(self, title: str, value: str):
        card = createFrame(
            self,
            theme=self._theme,
            fg_color=self._theme["surface"],
            corner_radius=int(self._theme["radius_md"]),
        )
        card.pack(fill="x", padx=18, pady=(0, 12))
        createLabel(
            card,
            title,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=14, pady=(12, 6))
        valueLabel = createLabel(
            card,
            value,
            theme=self._theme,
            font=("Segoe UI", 13, "bold"),
            wraplength=180,
        )
        valueLabel.pack(anchor="w", padx=14, pady=(0, 12))
        return valueLabel
