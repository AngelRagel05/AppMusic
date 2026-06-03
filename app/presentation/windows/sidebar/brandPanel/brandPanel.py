from __future__ import annotations

import customtkinter as ctk

from app.presentation.styles import createFrame, createLabel


class BrandPanel(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        badge = createFrame(
            self,
            theme=self._theme,
            fg_color=self._theme["primary"],
            corner_radius=16,
        )
        badge.pack(anchor="w")
        createLabel(
            badge,
            "AM",
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        ).pack(padx=14, pady=10)

        createLabel(
            self,
            "AppMusic",
            theme=self._theme,
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w", pady=(18, 4))
        createLabel(
            self,
            "Configuración musical",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
        ).pack(anchor="w")
