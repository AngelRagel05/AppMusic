from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from app.application.dto.localFolderDto import LocalFolderDto

from app.presentation.features.localLibrary.ui.localLibraryPage.localLibrariesSection.localLibrariesSection import (
    LocalLibrariesSection,
)
from app.presentation.styles import createFrame, getPageTheme
from app.presentation.widgets.pageHeader.pageHeader import PageHeader


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
        self.header.setActions("Actualizar canciones", "Escanear biblioteca")
        self.section = LocalLibrariesSection(content, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(28, 0))

    def onPrimaryActionRequested(self, callback: Callable[[], None]) -> None:
        self.header.primaryActionRequested.connect(callback)

    def onSecondaryActionRequested(self, callback: Callable[[], None]) -> None:
        self.header.secondaryActionRequested.connect(callback)

    def onBrowseFolderRequested(self, callback: Callable[[], None]) -> None:
        self.section.browseFolderButton.clicked.connect(callback)

    def onSaveFolderRequested(self, callback: Callable[[], None]) -> None:
        self.section.saveFolderButton.clicked.connect(callback)

    def onActivateFolderRequested(self, callback: Callable[[int], None]) -> None:
        self.section.activateRequested.connect(callback)

    def onEditFolderRequested(self, callback: Callable[[int], None]) -> None:
        self.section.editRequested.connect(callback)

    def onDeleteFolderRequested(self, callback: Callable[[int], None]) -> None:
        self.section.deleteRequested.connect(callback)

    def showFolders(self, localFolders: list[LocalFolderDto]) -> None:
        self.section.showFolders(localFolders)

    def showActiveFolder(self, activeFolder: LocalFolderDto | None) -> None:
        self.section.showActiveFolder(activeFolder)

    def folderPath(self) -> str:
        return self.section.folderPath()

    def folderDisplayName(self) -> str:
        return self.section.folderDisplayName()

    def setFolderPath(self, path: str) -> None:
        self.section.setFolderPath(path)

    def setFolderDisplayName(self, display_name: str) -> None:
        self.section.setFolderDisplayName(display_name)

    def setSaveMode(self, isEditing: bool) -> None:
        self.section.setSaveMode(isEditing)

    def clearForm(self) -> None:
        self.section.clearForm()

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.section.showStatusMessage(message, tone=tone)

    def focusPrimaryInput(self) -> None:
        self.section.focusPrimaryInput()

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
