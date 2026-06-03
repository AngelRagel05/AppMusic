from __future__ import annotations

import customtkinter as ctk

from app.presentation.features.youtubePlaylists.ui.youtubePlaylistsPage.youtubePlaylistsSection.youtubePlaylistsSection import (
    YoutubePlaylistsSection,
)
from app.presentation.shared.widgets.pageHeader.pageHeader import PageHeader
from app.presentation.uiTheme import createFrame, getPageTheme


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
        self.header.setActions(None, "Guardar playlist")
        self.section = YoutubePlaylistsSection(content, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(28, 0))

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
