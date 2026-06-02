from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import ActionButton, Signal, createLabel
from app.presentation.uiTheme.themePalette import ThemeTokens


class PageHeader(tk.Frame):
    def __init__(self, parent: tk.Misc, title: str, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["bg"])
        self.secondaryActionRequested = Signal()
        self.primaryActionRequested = Signal()
        self._theme = theme

        self.titleLabel = createLabel(
            self,
            title,
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        )
        self.activeFolderTitle = createLabel(
            self,
            "Biblioteca activa:",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            font=("Segoe UI", 10, "bold"),
        )
        self.activeFolderValue = createLabel(self, "Sin biblioteca", theme=self._theme)
        self.activePlaylistTitleLabel = createLabel(
            self,
            "Playlist principal:",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            font=("Segoe UI", 10, "bold"),
        )
        self.activePlaylistValue = createLabel(self, "Sin playlist", theme=self._theme)

        self.secondaryButton = ActionButton(self, variant="secondary", theme=self._theme)
        self.secondaryButton.clicked.connect(self.secondaryActionRequested.emit)
        self.primaryButton = ActionButton(self, theme=self._theme)
        self.primaryButton.clicked.connect(self.primaryActionRequested.emit)

        top_row = tk.Frame(self, bg=self._theme["bg"])
        top_row.pack(fill="x")
        self.titleLabel.pack(in_=top_row, side="left")
        self.primaryButton.widget.pack(in_=top_row, side="right")
        self.secondaryButton.widget.pack(in_=top_row, side="right", padx=(0, 12))

        context_row = tk.Frame(self, bg=self._theme["bg"])
        context_row.pack(fill="x", pady=(10, 0))
        self._build_context_chip(
            context_row,
            self.activeFolderTitle,
            self.activeFolderValue,
        ).pack(side="left", padx=(0, 12))
        self._build_context_chip(
            context_row,
            self.activePlaylistTitleLabel,
            self.activePlaylistValue,
        ).pack(side="left")

    def setTitle(self, title: str) -> None:
        self.titleLabel.configure(text=title)

    def setActiveFolderName(self, name: str) -> None:
        self.activeFolderValue.configure(text=name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.activePlaylistValue.configure(text=title)

    def setActions(self, secondary_label: str | None, primary_label: str | None) -> None:
        self._set_button_state(self.secondaryButton, secondary_label)
        self._set_button_state(self.primaryButton, primary_label)

    def _set_button_state(self, button: ActionButton, label: str | None) -> None:
        has_label = label is not None and label != ""
        if has_label:
            button.setText(label or "")
            button.widget.pack(side="right", padx=(0, 12) if button is self.secondaryButton else 0)
        else:
            button.widget.pack_forget()

    def _build_context_chip(
        self,
        parent: tk.Misc,
        title_label: tk.Label,
        value_label: tk.Label,
    ) -> tk.Frame:
        pill = tk.Frame(parent, bg=self._theme["surface"], padx=10, pady=6)
        title_label.configure(bg=self._theme["surface"])
        value_label.configure(bg=self._theme["surface"])
        title_label.pack(in_=pill, side="left")
        value_label.pack(in_=pill, side="left", padx=(6, 0))
        return pill
