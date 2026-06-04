from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto

from app.presentation.features.youtubePlaylists.ui.youtubePlaylistsPage.youtubePlaylistsSection.youtubePlaylistsSection import (
    YoutubePlaylistsSection,
)
from app.presentation.styles import createFrame, getPageTheme
from app.presentation.widgets.pageHeader.pageHeader import PageHeader


class YoutubePlaylistsPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self._theme = getPageTheme("youtubePlaylists")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=36)

        self.header = PageHeader(
            content,
            "Playlist YouTube",
            self._theme,
            subtitle="Mantén una playlist de referencia para sincronizar tu biblioteca musical",
        )
        self.header.setActions(None, "Importar items")
        self.section = YoutubePlaylistsSection(content, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(28, 0))

    def onPrimaryActionRequested(self, callback: Callable[[], None]) -> None:
        self.header.primaryActionRequested.connect(callback)

    def onSavePlaylistRequested(self, callback: Callable[[], None]) -> None:
        self.section.savePlaylistButton.clicked.connect(callback)

    def onActivatePlaylistRequested(self, callback: Callable[[int], None]) -> None:
        self.section.activateRequested.connect(callback)

    def onEditPlaylistRequested(self, callback: Callable[[int], None]) -> None:
        self.section.editRequested.connect(callback)

    def onDeletePlaylistRequested(self, callback: Callable[[int], None]) -> None:
        self.section.deleteRequested.connect(callback)

    def showPlaylists(self, youtubePlaylists: list[YoutubePlaylistDto]) -> None:
        self.section.showPlaylists(youtubePlaylists)

    def showActivePlaylist(self, activePlaylist: YoutubePlaylistDto | None) -> None:
        self.section.showActivePlaylist(activePlaylist)

    def playlistUrl(self) -> str:
        return self.section.playlistUrl()

    def playlistTitle(self) -> str:
        return self.section.playlistTitle()

    def setPlaylistUrl(self, value: str) -> None:
        self.section.setPlaylistUrl(value)

    def setPlaylistTitle(self, value: str) -> None:
        self.section.setPlaylistTitle(value)

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
