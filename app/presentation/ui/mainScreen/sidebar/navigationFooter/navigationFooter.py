from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import createLabel
from app.presentation.uiTheme.themePalette import ThemeTokens


class NavigationFooter(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["panel"])
        self._theme = theme

        title = createLabel(
            self,
            "Navegacion",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            font=("Segoe UI", 9, "bold"),
        )
        text = createLabel(
            self,
            "Cada seccion ocupa toda la vista principal.",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            wraplength=170,
        )

        title.pack(anchor="w")
        text.pack(anchor="w", pady=(4, 0))
