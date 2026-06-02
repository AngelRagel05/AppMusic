from __future__ import annotations

import customtkinter as ctk

from app.presentation.ui.mainScreen.pages.filtersPage.ignoredTermsSection.ignoredTermsSection import (
    IgnoredTermsSection,
)
from app.presentation.ui.mainScreen.shared.pageHeader.pageHeader import PageHeader
from app.presentation.uiTheme import createFrame, getPageTheme


class FiltersPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self._theme = getPageTheme("filters")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=36)

        self.header = PageHeader(
            content,
            "Filtros",
            self._theme,
            subtitle="Define términos ignorados para mejorar la limpieza y comparación musical",
        )
        self.header.setActions(None, None)
        self.section = IgnoredTermsSection(content, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(28, 0))

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
