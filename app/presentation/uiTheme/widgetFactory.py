from __future__ import annotations

import tkinter as tk

from app.presentation.uiTheme.signalSupport import Signal
from app.presentation.uiTheme.themePalette import BASE_THEME, ThemeTokens


class ActionButton:
    def __init__(
        self,
        parent: tk.Misc,
        text: str = "",
        variant: str = "primary",
        theme: ThemeTokens | None = None,
    ) -> None:
        self._theme = theme or BASE_THEME
        self.clicked = Signal()
        self.widget = tk.Button(
            parent,
            text=text,
            command=self.clicked.emit,
            cursor="hand2",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            activeforeground=self._theme["text"],
            highlightthickness=0,
        )
        applyButtonStyle(self.widget, variant, self._theme)

    def setText(self, value: str) -> None:
        self.widget.configure(text=value)


def applyButtonStyle(
    widget: tk.Button,
    variant: str,
    theme: ThemeTokens | None = None,
) -> None:
    activeTheme = theme or BASE_THEME
    colors = {
        "primary": (activeTheme["primary"], activeTheme["primary_hover"]),
        "secondary": (activeTheme["surface_alt"], activeTheme["surface"]),
        "danger": (activeTheme["danger"], "#B83A3A"),
    }
    bg, activeBg = colors.get(variant, colors["primary"])
    widget.configure(
        bg=bg,
        fg=activeTheme["text"],
        activebackground=activeBg,
        disabledforeground=activeTheme["text_muted"],
    )


def createFrame(
    parent: tk.Misc,
    *,
    theme: ThemeTokens | None = None,
    bg: str | None = None,
    **packKwargs,
) -> tk.Frame:
    activeTheme = theme or BASE_THEME
    frame = tk.Frame(parent, bg=bg or activeTheme["bg"], highlightthickness=0, bd=0)
    if packKwargs:
        frame.pack(**packKwargs)
    return frame


def createLabel(
    parent: tk.Misc,
    text: str,
    *,
    theme: ThemeTokens | None = None,
    fg: str | None = None,
    bg: str | None = None,
    font: tuple | None = None,
    anchor: str = "w",
    justify: str = "left",
    wraplength: int = 0,
) -> tk.Label:
    activeTheme = theme or BASE_THEME
    return tk.Label(
        parent,
        text=text,
        fg=fg or activeTheme["text"],
        bg=bg or parent.cget("bg"),
        font=font or ("Segoe UI", 10),
        anchor=anchor,
        justify=justify,
        wraplength=wraplength,
    )


def createEntry(
    parent: tk.Misc,
    *,
    theme: ThemeTokens | None = None,
    width: int = 24,
) -> tk.Entry:
    activeTheme = theme or BASE_THEME
    return tk.Entry(
        parent,
        width=width,
        bg=activeTheme["surface_alt"],
        fg=activeTheme["text"],
        insertbackground=activeTheme["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=activeTheme["border"],
        highlightcolor=activeTheme["accent"],
    )


def createOptionMenu(
    parent: tk.Misc,
    variable: tk.StringVar,
    values: tuple[str, ...],
    *,
    theme: ThemeTokens | None = None,
) -> tk.OptionMenu:
    activeTheme = theme or BASE_THEME
    menu = tk.OptionMenu(parent, variable, *values)
    menu.configure(
        bg=activeTheme["surface_alt"],
        fg=activeTheme["text"],
        activebackground=activeTheme["surface"],
        activeforeground=activeTheme["text"],
        relief="flat",
        highlightthickness=0,
        bd=0,
    )
    menu["menu"].configure(
        bg=activeTheme["surface_alt"],
        fg=activeTheme["text"],
        activebackground=activeTheme["accent_soft"],
        activeforeground=activeTheme["text"],
    )
    return menu


def setStatusLabelTone(
    label: tk.Label,
    tone: str,
    theme: ThemeTokens | None = None,
) -> None:
    activeTheme = theme or BASE_THEME
    fgMap = {
        "success": activeTheme["success"],
        "error": activeTheme["danger"],
        "info": activeTheme["accent"],
        "idle": activeTheme["text_secondary"],
        "ready": activeTheme["success"],
    }
    label.configure(fg=fgMap.get(tone, activeTheme["text_secondary"]))


def clearChildren(widget: tk.Misc) -> None:
    for child in widget.winfo_children():
        child.destroy()


def bindRecursive(widget: tk.Misc, sequence: str, callback) -> None:
    widget.bind(sequence, callback)
    for child in widget.winfo_children():
        bindRecursive(child, sequence, callback)
