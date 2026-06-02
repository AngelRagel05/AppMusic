from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import BASE_THEME, Signal
from app.presentation.uiTheme.themePalette import ThemeTokens
from app.presentation.ui.mainScreen.sidebar.brandPanel.brandPanel import BrandPanel
from app.presentation.ui.mainScreen.sidebar.contextSummary.contextSummary import (
    ContextSummary,
)
from app.presentation.ui.mainScreen.sidebar.navigationFooter.navigationFooter import (
    NavigationFooter,
)
from app.presentation.ui.mainScreen.sidebar.navigationMenu.navigationMenu import (
    NavigationMenu,
)


class Sidebar(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens | None = None) -> None:
        self._theme = theme or BASE_THEME
        super().__init__(parent, bg=self._theme["panel"], width=212, padx=14, pady=18)
        self.grid_propagate(False)
        self.overviewRequested = Signal()
        self.localLibrariesRequested = Signal()
        self.youtubePlaylistsRequested = Signal()
        self.ignoredTermsRequested = Signal()

        self.brandPanel = BrandPanel(self, self._theme)
        self.navigationMenu = NavigationMenu(self, self._theme)
        self.contextSummary = ContextSummary(self, self._theme)
        self.navigationFooter = NavigationFooter(self, self._theme)

        self.navigationMenu.overviewRequested.connect(self.overviewRequested.emit)
        self.navigationMenu.localLibrariesRequested.connect(self.localLibrariesRequested.emit)
        self.navigationMenu.youtubePlaylistsRequested.connect(
            self.youtubePlaylistsRequested.emit
        )
        self.navigationMenu.ignoredTermsRequested.connect(self.ignoredTermsRequested.emit)

        self.brandPanel.pack(fill="x")
        self.navigationMenu.pack(fill="x", pady=(18, 18))
        self.contextSummary.pack(fill="x")
        self.navigationFooter.pack(fill="x", side="bottom", pady=(18, 0))
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
