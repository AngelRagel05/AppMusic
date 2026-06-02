from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import createLabel
from app.presentation.uiTheme.themePalette import ThemeTokens


class BrandPanel(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["panel"])
        self._theme = theme

        badge = createLabel(
            self,
            "AM",
            theme=self._theme,
            bg=self._theme["primary"],
            font=("Segoe UI", 12, "bold"),
            anchor="center",
        )
        badge.configure(width=4, pady=8)
        title = createLabel(self, "AppMusic", theme=self._theme, font=("Segoe UI", 14, "bold"))
        subtitle = createLabel(
            self,
            "Configuracion musical",
            theme=self._theme,
            fg=self._theme["text_secondary"],
        )

        badge.pack(anchor="w")
        title.pack(anchor="w", pady=(12, 2))
        subtitle.pack(anchor="w")
