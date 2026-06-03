from __future__ import annotations

import customtkinter as ctk

from app.presentation.shell.appShell.appShell import AppShell


class MainWindow:
    def __init__(self) -> None:
        self.window = ctk.CTk()
        self._page = AppShell(self.window)
        self._page.pack(fill="both", expand=True)

    @property
    def page(self) -> AppShell:
        return self._page

    def show(self) -> None:
        self.window.deiconify()

    def mainloop(self) -> None:
        self.window.mainloop()
