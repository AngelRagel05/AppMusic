from __future__ import annotations

import customtkinter as ctk

from app.presentation.uiTheme import createLabel


class NavigationFooter(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)

        createLabel(
            self,
            "AppMusic organiza bibliotecas, playlists y filtros desde una única consola.",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12),
            wraplength=190,
        ).pack(anchor="w")
