from __future__ import annotations

import customtkinter as ctk

from app.presentation.uiTheme import ActionButton, Signal, createFrame, createLabel


class PageHeader(ctk.CTkFrame):
    def __init__(self, parent, title: str, theme, subtitle: str | None = None) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.secondaryActionRequested = Signal()
        self.primaryActionRequested = Signal()

        self._subtitleText = subtitle or ""

        self.grid_columnconfigure(0, weight=1)

        titleGroup = createFrame(self, theme=self._theme, fg_color="transparent")
        titleGroup.grid(row=0, column=0, sticky="w")
        self.titleLabel = createLabel(
            titleGroup,
            title,
            theme=self._theme,
            font=("Segoe UI", 28, "bold"),
        )
        self.titleLabel.pack(anchor="w")
        self.subtitleLabel = createLabel(
            titleGroup,
            self._subtitleText,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 14),
        )
        self.subtitleLabel.pack(anchor="w", pady=(6, 0))

        self.primaryButton = ActionButton(self, theme=self._theme, variant="primary")
        self.primaryButton.clicked.connect(self.primaryActionRequested.emit)
        self.secondaryButton = ActionButton(self, theme=self._theme, variant="secondary")
        self.secondaryButton.clicked.connect(self.secondaryActionRequested.emit)
        self.secondaryButton.widget.grid(row=0, column=1, sticky="e", padx=(0, 12))
        self.primaryButton.widget.grid(row=0, column=2, sticky="e")

        contextRow = createFrame(self, theme=self._theme, fg_color="transparent")
        contextRow.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        self.activeFolderBadge = self._build_context_badge(
            contextRow,
            "Biblioteca activa",
            "Sin biblioteca configurada",
        )
        self.activeFolderBadge.pack(side="left", padx=(0, 12))
        self.activePlaylistBadge = self._build_context_badge(
            contextRow,
            "Playlist activa",
            "Sin playlist configurada",
        )
        self.activePlaylistBadge.pack(side="left")

    def setTitle(self, title: str) -> None:
        self.titleLabel.configure(text=title)

    def setSubtitle(self, subtitle: str) -> None:
        self.subtitleLabel.configure(text=subtitle)

    def setActiveFolderName(self, name: str) -> None:
        self.activeFolderValue.configure(text=name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.activePlaylistValue.configure(text=title)

    def setActions(self, secondary_label: str | None, primary_label: str | None) -> None:
        self._set_button_state(self.secondaryButton, secondary_label)
        self._set_button_state(self.primaryButton, primary_label)

    def _set_button_state(self, button: ActionButton, label: str | None) -> None:
        hasLabel = label is not None and label != ""
        if hasLabel:
            button.setText(label or "")
            button.widget.grid()
        else:
            button.widget.grid_remove()

    def _build_context_badge(self, parent, label: str, value: str):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_md"]),
            border_width=1,
            border_color=self._theme["border"],
        )
        createLabel(
            card,
            label,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=14, pady=(10, 4))
        valueLabel = createLabel(
            card,
            value,
            theme=self._theme,
            font=("Segoe UI", 13, "bold"),
        )
        valueLabel.pack(anchor="w", padx=14, pady=(0, 10))

        if "Biblioteca" in label:
            self.activeFolderValue = valueLabel
        else:
            self.activePlaylistValue = valueLabel
        return card
