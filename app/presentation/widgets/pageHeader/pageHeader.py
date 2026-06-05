from __future__ import annotations

import customtkinter as ctk

from app.presentation.styles import ActionButton, Signal, createFrame, createLabel


class PageHeader(ctk.CTkFrame):
    def __init__(self, parent, title: str, theme, subtitle: str | None = None) -> None:
        self._theme = theme
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)
        self.secondaryActionRequested = Signal()
        self.primaryActionRequested = Signal()

        self._subtitleText = subtitle or ""

        self.grid_columnconfigure(0, weight=1)

        titleGroup = createFrame(self, theme=self._theme, fg_color=self._theme["bg"])
        titleGroup.grid(row=0, column=0, sticky="w")
        self.titleLabel = createLabel(
            titleGroup,
            title,
            theme=self._theme,
            font=("Segoe UI", int(self._theme["title_size"]), "bold"),
        )
        self.titleLabel.pack(anchor="w")
        self.subtitleLabel = createLabel(
            titleGroup,
            self._subtitleText,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", int(self._theme["subtitle_size"])),
        )
        self.subtitleLabel.pack(anchor="w", pady=(4, 0))

        self.primaryButton = ActionButton(self, theme=self._theme, variant="primary")
        self.primaryButton.clicked.connect(self.primaryActionRequested.emit)
        self.secondaryButton = ActionButton(self, theme=self._theme, variant="secondary")
        self.secondaryButton.clicked.connect(self.secondaryActionRequested.emit)
        self.secondaryButton.widget.grid(row=0, column=1, sticky="e", padx=(0, 8))
        self.primaryButton.widget.grid(row=0, column=2, sticky="e")

    def setTitle(self, title: str) -> None:
        self.titleLabel.configure(text=title)

    def setSubtitle(self, subtitle: str) -> None:
        self.subtitleLabel.configure(text=subtitle)

    def setActiveFolderName(self, name: str) -> None:
        return None

    def setActivePlaylistTitle(self, title: str) -> None:
        return None

    def setActions(self, secondary_label: str | None, primary_label: str | None) -> None:
        self._set_button_state(self.secondaryButton, secondary_label)
        self._set_button_state(self.primaryButton, primary_label)

    def setContextVisible(self, visible: bool) -> None:
        return None

    def _set_button_state(self, button: ActionButton, label: str | None) -> None:
        hasLabel = label is not None and label != ""
        if hasLabel:
            button.setText(label or "")
            button.widget.grid()
        else:
            button.widget.grid_remove()

