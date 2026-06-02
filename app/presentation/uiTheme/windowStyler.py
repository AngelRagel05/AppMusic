from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from app.presentation.uiTheme.themePalette import BASE_THEME, ThemeTokens


def configureRootWindow(
    window: tk.Tk,
    title: str,
    theme: ThemeTokens | None = None,
) -> None:
    activeTheme = theme or BASE_THEME
    window.title(title)
    window.configure(bg=activeTheme["bg"])
    window.geometry("1280x820")
    try:
        window.state("zoomed")
    except tk.TclError:
        pass

    defaultFont = tkfont.nametofont("TkDefaultFont")
    defaultFont.configure(family="Segoe UI", size=10)
    textFont = tkfont.nametofont("TkTextFont")
    textFont.configure(family="Segoe UI", size=10)
