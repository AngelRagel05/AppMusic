from __future__ import annotations

import customtkinter as ctk

from app.presentation.shared.theme.themePalette import BASE_THEME, ThemeTokens


def configureRootWindow(
    window: ctk.CTk,
    title: str,
    theme: ThemeTokens | None = None,
) -> None:
    activeTheme = theme or BASE_THEME
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    window.title(title)
    window.configure(fg_color=activeTheme["bg"])
    window.geometry("1440x940")
    window.minsize(1280, 820)
    try:
        window.state("zoomed")
    except Exception:
        pass
