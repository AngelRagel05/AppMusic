from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from app.application.dto.ignoredTermDto import IgnoredTermDto

from app.presentation.features.ignoredTerms.ui.ignoredTermsPage.ignoredTermsSection.ignoredTermsSection import (
    IgnoredTermsSection,
)
from app.presentation.styles import createFrame, getPageTheme
from app.presentation.widgets.pageHeader.pageHeader import PageHeader


class IgnoredTermsPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self._theme = getPageTheme("ignoredTerms")
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

    def onSaveTermRequested(self, callback: Callable[[], None]) -> None:
        self.section.createButton.clicked.connect(callback)

    def onEditTermRequested(self, callback: Callable[[int], None]) -> None:
        self.section.editRequested.connect(callback)

    def onToggleTermRequested(self, callback: Callable[[int], None]) -> None:
        self.section.toggleRequested.connect(callback)

    def onDeleteTermRequested(self, callback: Callable[[int], None]) -> None:
        self.section.deleteRequested.connect(callback)

    def showTerms(self, ignoredTerms: list[IgnoredTermDto]) -> None:
        self.section.showTerms(ignoredTerms)

    def termText(self) -> str:
        return self.section.termText()

    def termScope(self) -> str:
        return self.section.termScope()

    def termLanguage(self) -> str:
        return self.section.termLanguage()

    def clearTermInput(self) -> None:
        self.section.clearTermInput()

    def setTermText(self, value: str) -> None:
        self.section.setTermText(value)

    def setTermScope(self, value: str) -> None:
        self.section.setTermScope(value)

    def setTermLanguage(self, value: str) -> None:
        self.section.setTermLanguage(value)

    def setSaveMode(self, isEditing: bool) -> None:
        self.section.setSaveMode(isEditing)

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.section.showStatusMessage(message, tone=tone)

    def focusPrimaryInput(self) -> None:
        self.section.focusPrimaryInput()

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
