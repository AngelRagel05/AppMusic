from __future__ import annotations

import customtkinter as ctk

from app.presentation.styles import createFrame, createLabel
from app.presentation.styles.themePalette import ThemeTokens
from app.presentation.widgets.statusBadge.statusBadge import StatusBadge


class StatCard(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        title: str,
        value: str,
        theme: ThemeTokens,
        badge_text: str | None = None,
        badge_tone: str = "idle",
    ) -> None:
        self._theme = theme
        super().__init__(
            parent,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_lg"]),
            border_width=1,
            border_color=self._theme["border"],
        )

        header = createFrame(self, theme=self._theme, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 8))
        self._titleLabel = createLabel(
            header,
            title,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", int(self._theme["label_size"]), "bold"),
        )
        self._titleLabel.pack(side="left")
        self._badge = None
        if badge_text:
            self._badge = StatusBadge(header, badge_text, badge_tone, self._theme)
            self._badge.pack(side="right")

        self._valueLabel = createLabel(
            self,
            value,
            theme=self._theme,
            text_color=self._theme["text"],
            font=("Segoe UI", int(self._theme["value_size"]), "bold"),
            wraplength=280,
        )
        self._valueLabel.pack(fill="x", padx=20, pady=(0, 18))

    def setValue(self, value: str) -> None:
        self._valueLabel.configure(text=value)

    def setBadge(self, text: str, tone: str) -> None:
        if self._badge is None:
            self._badge = StatusBadge(self._titleLabel.master, text, tone, self._theme)
            self._badge.pack(side="right")
            return
        self._badge.setStatus(text, tone)
