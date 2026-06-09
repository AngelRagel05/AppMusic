from __future__ import annotations

import customtkinter as ctk

from app.presentation.styles import BASE_THEME, Signal
from app.presentation.windows.sidebar.brandPanel.brandPanel import BrandPanel
from app.presentation.windows.sidebar.contextSummary.contextSummary import (
    ContextSummary,
)
from app.presentation.windows.sidebar.navigationFooter.navigationFooter import (
    NavigationFooter,
)
from app.presentation.windows.sidebar.navigationMenu.navigationMenu import (
    NavigationMenu,
)


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, theme=None) -> None:
        self._theme = theme or BASE_THEME
        super().__init__(
            parent,
            width=int(self._theme["sidebar_width"]),
            fg_color=self._theme["sidebar"],
            corner_radius=0,
            border_width=0,
        )
        self.grid_propagate(False)
        self.overviewRequested = Signal()
        self.comparisonRequested = Signal()
        self.localLibraryRequested = Signal()
        self.youtubePlaylistsRequested = Signal()
        self.ignoredTermsRequested = Signal()

        self.grid_rowconfigure(2, weight=1)

        self.brandPanel = BrandPanel(self, self._theme)
        self.navigationMenu = NavigationMenu(self, self._theme)
        self.contextSummary = ContextSummary(self, self._theme)
        self.navigationFooter = NavigationFooter(self, self._theme)

        self.navigationMenu.overviewRequested.connect(self.overviewRequested.emit)
        self.navigationMenu.comparisonRequested.connect(self.comparisonRequested.emit)
        self.navigationMenu.localLibraryRequested.connect(self.localLibraryRequested.emit)
        self.navigationMenu.youtubePlaylistsRequested.connect(
            self.youtubePlaylistsRequested.emit
        )
        self.navigationMenu.ignoredTermsRequested.connect(self.ignoredTermsRequested.emit)

        self.brandPanel.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 18))
        self.navigationMenu.grid(row=1, column=0, sticky="ew", padx=14)
        self.contextSummary.grid(row=2, column=0, sticky="sew", padx=14, pady=(12, 8))
        self.navigationFooter.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 14))
        self.setActiveSection("overview")

    def setActiveSection(self, section: str) -> None:
        self.navigationMenu.setActiveSection(section)

    def showActiveFolderName(self, display_name: str) -> None:
        self.contextSummary.showActiveFolderName(display_name)

    def showSongCount(self, value: str) -> None:
        self.contextSummary.showSongCount(value)

    def showActivePlaylistTitle(self, title: str) -> None:
        self.contextSummary.showActivePlaylistTitle(title)

    def showSyncStatus(self, status: str, state: str = "idle") -> None:
        self.contextSummary.showSyncStatus(status, state=state)
