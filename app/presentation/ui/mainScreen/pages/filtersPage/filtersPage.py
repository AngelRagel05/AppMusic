from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import getPageTheme
from app.presentation.ui.mainScreen.pages.filtersPage.ignoredTermsSection.ignoredTermsSection import (
    IgnoredTermsSection,
)
from app.presentation.ui.mainScreen.shared.pageHeader.pageHeader import PageHeader


class FiltersPage(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        self._theme = getPageTheme("filters")
        super().__init__(parent, bg=self._theme["bg"], padx=28, pady=20)
        self.header = PageHeader(self, "Filtros", self._theme)
        self.header.setActions(None, None)
        self.section = IgnoredTermsSection(self, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(14, 0))

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
