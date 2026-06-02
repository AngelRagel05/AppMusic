from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import Signal
from app.presentation.uiTheme.themePalette import ThemeTokens


class NavigationMenu(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["panel"])
        self._theme = theme
        self.overviewRequested = Signal()
        self.localLibrariesRequested = Signal()
        self.youtubePlaylistsRequested = Signal()
        self.ignoredTermsRequested = Signal()

        self._buttons = {
            "overview": self._build_button("Resumen", self.overviewRequested.emit),
            "libraries": self._build_button("Biblioteca local", self.localLibrariesRequested.emit),
            "playlists": self._build_button("Playlist YouTube", self.youtubePlaylistsRequested.emit),
            "filters": self._build_button("Filtros", self.ignoredTermsRequested.emit),
        }

        for button in self._buttons.values():
            button.pack(fill="x", pady=(0, 8))

    def setActiveSection(self, section: str) -> None:
        for key, button in self._buttons.items():
            button.configure(
                bg=self._theme["accent_soft"] if key == section else self._theme["surface_alt"],
                fg=self._theme["text"],
            )

    def _build_button(self, label: str, handler) -> tk.Button:
        return tk.Button(
            self,
            text=label,
            command=handler,
            cursor="hand2",
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            anchor="w",
            bg=self._theme["surface_alt"],
            fg=self._theme["text"],
            activebackground=self._theme["surface"],
            activeforeground=self._theme["text"],
            highlightthickness=0,
        )
