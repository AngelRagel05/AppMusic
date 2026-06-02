from __future__ import annotations

import tkinter as tk

from app.presentation.ui.mainScreen.appLayout.appLayout import AppLayout


class MainWindow:
    def __init__(self) -> None:
        self.window = tk.Tk()
        self._page = AppLayout(self.window)
        self._page.pack(fill="both", expand=True)

    @property
    def page(self) -> AppLayout:
        return self._page

    def show(self) -> None:
        self.window.deiconify()

    def mainloop(self) -> None:
        self.window.mainloop()
