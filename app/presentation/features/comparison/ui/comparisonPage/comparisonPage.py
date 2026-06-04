from __future__ import annotations

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.youtubePlaylistItemDto import YoutubePlaylistItemDto
from app.presentation.features.comparison.ui.comparisonPage.comparisonSplitSection.comparisonSplitSection import (
    ComparisonSplitSection,
)
from app.presentation.styles import createFrame, getPageTheme
from app.presentation.widgets.pageHeader.pageHeader import PageHeader


class ComparisonPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        self._theme = getPageTheme("overview")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=36)

        self.header = PageHeader(
            content,
            "Comparacion",
            self._theme,
            subtitle="Consulta en paralelo las canciones de tu biblioteca activa y los items importados de la playlist activa",
        )
        self.header.setActions(None, None)
        self.section = ComparisonSplitSection(content, self._theme)

        self.header.pack(fill="x")
        self.section.pack(fill="both", expand=True, pady=(28, 0))

    def showLocalSongs(self, local_songs: list[LocalSongDto]) -> None:
        self.section.showLocalSongs(local_songs)

    def showYoutubePlaylistItems(
        self,
        youtube_playlist_items: list[YoutubePlaylistItemDto],
    ) -> None:
        self.section.showYoutubePlaylistItems(youtube_playlist_items)

    def setActiveFolderName(self, name: str) -> None:
        self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.header.setActivePlaylistTitle(title)
