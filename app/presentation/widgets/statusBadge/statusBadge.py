from __future__ import annotations

import customtkinter as ctk

from app.presentation.styles import createLabel
from app.presentation.styles.themePalette import ThemeTokens


class StatusBadge(ctk.CTkFrame):
    def __init__(self, parent, text: str, tone: str, theme: ThemeTokens) -> None:
        self._theme = theme
        super().__init__(
            parent,
            fg_color=self._badge_background(tone),
            corner_radius=int(self._theme["radius_sm"]),
            border_width=0,
        )
        self._label = createLabel(
            self,
            text,
            theme=self._theme,
            text_color=self._badge_text(tone),
            font=("Segoe UI", 10, "bold"),
        )
        self._label.pack(padx=8, pady=3)

    def setStatus(self, text: str, tone: str) -> None:
        self.configure(fg_color=self._badge_background(tone))
        self._label.configure(text=text, text_color=self._badge_text(tone))

    def _badge_background(self, tone: str) -> str:
        mapping = {
            "success": self._theme["success"],
            "ready": self._theme["success"],
            "error": self._theme["danger"],
            "info": self._theme["accent_soft"],
            "idle": self._theme["surface"],
        }
        return str(mapping.get(tone, self._theme["surface"]))

    def _badge_text(self, tone: str) -> str:
        if tone in {"success", "ready", "error"}:
            return str(self._theme["text"])
        if tone == "info":
            return str(self._theme["accent"])
        return str(self._theme["text_secondary"])
