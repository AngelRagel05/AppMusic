from __future__ import annotations

import customtkinter as ctk

from app.presentation.uiTheme import Signal


class NavigationMenu(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.overviewRequested = Signal()
        self.localLibrariesRequested = Signal()
        self.youtubePlaylistsRequested = Signal()
        self.ignoredTermsRequested = Signal()

        self._buttons = {
            "overview": self._build_button("Resumen", self.overviewRequested.emit),
            "libraries": self._build_button(
                "Biblioteca local",
                self.localLibrariesRequested.emit,
            ),
            "playlists": self._build_button(
                "Playlist YouTube",
                self.youtubePlaylistsRequested.emit,
            ),
            "filters": self._build_button("Filtros", self.ignoredTermsRequested.emit),
        }

        for button in self._buttons.values():
            button.pack(fill="x", pady=(0, 10))

    def setActiveSection(self, section: str) -> None:
        for key, button in self._buttons.items():
            isActive = key == section
            button.configure(
                fg_color=self._theme["accent_soft"] if isActive else "transparent",
                hover_color=self._theme["hover"],
                text_color=self._theme["text"] if isActive else self._theme["text_secondary"],
            )

    def _build_button(self, label: str, handler):
        return ctk.CTkButton(
            self,
            text=label,
            command=handler,
            anchor="w",
            height=int(self._theme["sidebar_button_height"]),
            corner_radius=int(self._theme["radius_md"]),
            fg_color="transparent",
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13, "bold"),
        )
