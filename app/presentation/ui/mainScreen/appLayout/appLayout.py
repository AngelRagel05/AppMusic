from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme import BASE_THEME
from app.presentation.ui.mainScreen.pages.filtersPage.filtersPage import FiltersPage
from app.presentation.ui.mainScreen.pages.libraryLocalPage.libraryLocalPage import (
    LibraryLocalPage,
)
from app.presentation.ui.mainScreen.pages.overviewPage.overviewPage import OverviewPage
from app.presentation.ui.mainScreen.pages.playlistYouTubePage.playlistYouTubePage import (
    PlaylistYouTubePage,
)
from app.presentation.ui.mainScreen.sidebar.sidebar.sidebar import Sidebar


class AppLayout(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=BASE_THEME["bg"])

        self.sidebar = Sidebar(self)
        self.pagesHost = tk.Frame(self, bg=BASE_THEME["bg"])

        self.overviewPage = OverviewPage(self.pagesHost)
        self.libraryPage = LibraryLocalPage(self.pagesHost)
        self.playlistPage = PlaylistYouTubePage(self.pagesHost)
        self.filtersPage = FiltersPage(self.pagesHost)

        self.heroSection = self.overviewPage.header
        self.localLibrariesSection = self.libraryPage.section
        self.youtubePlaylistsSection = self.playlistPage.section
        self.ignoredTermsSection = self.filtersPage.section

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.pagesHost.grid(row=0, column=1, sticky="nsew")
        self.pagesHost.grid_rowconfigure(0, weight=1)
        self.pagesHost.grid_columnconfigure(0, weight=1)

        for page in (
            self.overviewPage,
            self.libraryPage,
            self.playlistPage,
            self.filtersPage,
        ):
            page.grid(row=0, column=0, sticky="nsew")

        self.sidebar.overviewRequested.connect(lambda: self.showPage("overview"))
        self.sidebar.localLibrariesRequested.connect(lambda: self.showPage("libraries"))
        self.sidebar.youtubePlaylistsRequested.connect(lambda: self.showPage("playlists"))
        self.sidebar.ignoredTermsRequested.connect(lambda: self.showPage("filters"))

        self.overviewPage.header.secondaryActionRequested.connect(
            lambda: self.showPage("libraries", focus_input=True)
        )
        self.overviewPage.header.primaryActionRequested.connect(
            lambda: self.showPage("playlists", focus_input=True)
        )
        self.libraryPage.header.secondaryActionRequested.connect(
            lambda: self.showPage("libraries", focus_input=True)
        )
        self.playlistPage.header.secondaryActionRequested.connect(
            lambda: self.showPage("playlists", focus_input=True)
        )

        self.showPage("overview")

    def showPage(self, page_name: str, focus_input: bool = False) -> None:
        page_map = {
            "overview": self.overviewPage,
            "libraries": self.libraryPage,
            "playlists": self.playlistPage,
            "filters": self.filtersPage,
        }
        page = page_map[page_name]
        page.tkraise()
        self.sidebar.setActiveSection(page_name)
        section = getattr(page, "section", None)
        if focus_input and section is not None and hasattr(section, "focusPrimaryInput"):
            section.focusPrimaryInput()

    def setActiveFolderName(self, name: str) -> None:
        self.overviewPage.setActiveFolderName(name)
        self.libraryPage.setActiveFolderName(name)
        self.playlistPage.setActiveFolderName(name)
        self.filtersPage.setActiveFolderName(name)
        self.sidebar.showActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.overviewPage.setActivePlaylistTitle(title)
        self.libraryPage.setActivePlaylistTitle(title)
        self.playlistPage.setActivePlaylistTitle(title)
        self.filtersPage.setActivePlaylistTitle(title)
        self.sidebar.showActivePlaylistTitle(title)

    def setSongCount(self, value: str) -> None:
        self.overviewPage.setSongCount(value)
        self.sidebar.showSongCount(value)

    def setSyncStatus(self, value: str, state: str = "idle") -> None:
        self.overviewPage.setSyncStatus(value)
        self.sidebar.showSyncStatus(value, state=state)

    def setLastAction(self, value: str) -> None:
        self.overviewPage.setLastAction(value)
