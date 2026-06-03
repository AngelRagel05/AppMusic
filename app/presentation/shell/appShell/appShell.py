from __future__ import annotations

import customtkinter as ctk

from app.presentation.features.ignoredTerms.ui.ignoredTermsPage.ignoredTermsPage import (
    IgnoredTermsPage,
)
from app.presentation.features.localLibrary.ui.localLibraryPage.localLibraryPage import (
    LocalLibraryPage,
)
from app.presentation.features.overview.ui.overviewPage.overviewPage import OverviewPage
from app.presentation.features.youtubePlaylists.ui.youtubePlaylistsPage.youtubePlaylistsPage import (
    YoutubePlaylistsPage,
)
from app.presentation.shell.sidebar.sidebar.sidebar import Sidebar
from app.presentation.shared.theme import BASE_THEME, createFrame


class AppShell(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent, fg_color=BASE_THEME["bg"], corner_radius=0)

        self.sidebar = Sidebar(self, BASE_THEME)
        self.pagesHost = createFrame(self, theme=BASE_THEME, fg_color=BASE_THEME["bg"])

        self.overviewPage = OverviewPage(self.pagesHost)
        self.localLibraryPage = LocalLibraryPage(self.pagesHost)
        self.youtubePlaylistsPage = YoutubePlaylistsPage(self.pagesHost)
        self.ignoredTermsPage = IgnoredTermsPage(self.pagesHost)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.pagesHost.grid(row=0, column=1, sticky="nsew")
        self.pagesHost.grid_rowconfigure(0, weight=1)
        self.pagesHost.grid_columnconfigure(0, weight=1)

        for page in (
            self.overviewPage,
            self.localLibraryPage,
            self.youtubePlaylistsPage,
            self.ignoredTermsPage,
        ):
            page.grid(row=0, column=0, sticky="nsew")

        self.sidebar.overviewRequested.connect(lambda: self.showPage("overview"))
        self.sidebar.localLibraryRequested.connect(lambda: self.showPage("localLibrary"))
        self.sidebar.youtubePlaylistsRequested.connect(
            lambda: self.showPage("youtubePlaylists")
        )
        self.sidebar.ignoredTermsRequested.connect(lambda: self.showPage("ignoredTerms"))

        self.overviewPage.onScanLibraryRequested(
            lambda: self.showPage("localLibrary", focus_input=True)
        )
        self.localLibraryPage.onPrimaryActionRequested(
            lambda: self.showPage("localLibrary", focus_input=True)
        )
        self.youtubePlaylistsPage.onPrimaryActionRequested(
            lambda: self.showPage("youtubePlaylists", focus_input=True)
        )

        self.showPage("overview")

    def showPage(self, page_name: str, focus_input: bool = False) -> None:
        page_map = {
            "overview": self.overviewPage,
            "localLibrary": self.localLibraryPage,
            "youtubePlaylists": self.youtubePlaylistsPage,
            "ignoredTerms": self.ignoredTermsPage,
        }
        page = page_map[page_name]
        page.tkraise()
        self.sidebar.setActiveSection(page_name)
        if focus_input and hasattr(page, "focusPrimaryInput"):
            page.focusPrimaryInput()

    def setActiveFolderName(self, name: str) -> None:
        self.overviewPage.setActiveFolderName(name)
        self.localLibraryPage.setActiveFolderName(name)
        self.youtubePlaylistsPage.setActiveFolderName(name)
        self.ignoredTermsPage.setActiveFolderName(name)
        self.sidebar.showActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.overviewPage.setActivePlaylistTitle(title)
        self.localLibraryPage.setActivePlaylistTitle(title)
        self.youtubePlaylistsPage.setActivePlaylistTitle(title)
        self.ignoredTermsPage.setActivePlaylistTitle(title)
        self.sidebar.showActivePlaylistTitle(title)

    def setSongCount(self, value: str) -> None:
        self.overviewPage.setSongCount(value)
        self.sidebar.showSongCount(value)

    def setSyncStatus(self, value: str, state: str = "idle") -> None:
        self.overviewPage.setSyncStatus(value, state=state)
        self.sidebar.showSyncStatus(value, state=state)

    def setLastAction(self, value: str) -> None:
        self.overviewPage.setLastAction(value)
