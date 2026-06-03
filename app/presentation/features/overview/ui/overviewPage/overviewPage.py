from __future__ import annotations

import customtkinter as ctk

from app.presentation.features.overview.ui.overviewPage.dashboardView import DashboardView
from app.presentation.uiTheme import createFrame, getPageTheme


class OverviewPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self._theme = getPageTheme("overview")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=36)

        self.dashboard = DashboardView(content, self._theme)
        self.dashboard.pack(fill="both", expand=True)

    def setActiveFolderName(self, name: str) -> None:
        self.dashboard.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.dashboard.setActivePlaylistTitle(title)

    def setSongCount(self, value: str) -> None:
        self.dashboard.setSongCount(value)

    def setSyncStatus(self, value: str, state: str = "idle") -> None:
        self.dashboard.setSyncStatus(value, state)

    def setLastAction(self, value: str) -> None:
        self.dashboard.setLastAction(value)
