from __future__ import annotations

import customtkinter as ctk

from app.presentation.features.localLibrary.ui.localLibraryPage.localLibrariesSection.localLibrariesSection import (
    LocalLibrariesSection,
)
from app.presentation.shared.widgets.pageHeader.pageHeader import PageHeader
from app.presentation.shared.theme import createFrame, getPageTheme


class LocalLibraryPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self._theme = getPageTheme("localLibrary")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=36)

        self.header = PageHeader(
            content,
            "Biblioteca local",
            self._theme,
            subtitle="Gestiona la carpeta principal y el conjunto de bibliotecas guardadas",
        )
        self.header.setActions(None, "Escanear biblioteca")
        self.section = LocalLibrariesSection(content, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(28, 0))

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
