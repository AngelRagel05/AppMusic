from __future__ import annotations

import customtkinter as ctk

from app.presentation.shared.theme.signalSupport import Signal
from app.presentation.shared.theme.themePalette import BASE_THEME, ThemeTokens


class ActionButton:
    def __init__(
        self,
        parent,
        text: str = "",
        variant: str = "primary",
        theme: ThemeTokens | None = None,
        height: int | None = None,
    ) -> None:
        self._theme = theme or BASE_THEME
        self.clicked = Signal()
        self.widget = ctk.CTkButton(
            parent,
            text=text,
            command=self.clicked.emit,
            corner_radius=int(self._theme["radius_md"]),
            height=height or int(self._theme["button_height"]),
            border_width=0,
            font=("Segoe UI", 13, "bold"),
            anchor="center",
        )
        applyButtonStyle(self.widget, variant, self._theme)

    def setText(self, value: str) -> None:
        self.widget.configure(text=value)

    def setEnabled(self, enabled: bool) -> None:
        self.widget.configure(state="normal" if enabled else "disabled")


def applyButtonStyle(
    widget,
    variant: str,
    theme: ThemeTokens | None = None,
) -> None:
    activeTheme = theme or BASE_THEME
    palette = {
        "primary": {
            "fg_color": activeTheme["primary"],
            "hover_color": activeTheme["primary_hover"],
            "text_color": activeTheme["text"],
            "border_color": activeTheme["primary"],
        },
        "secondary": {
            "fg_color": activeTheme["surface"],
            "hover_color": activeTheme["hover"],
            "text_color": activeTheme["text_secondary"],
            "border_color": activeTheme["border"],
        },
        "ghost": {
            "fg_color": activeTheme["accent_soft"],
            "hover_color": activeTheme["hover"],
            "text_color": activeTheme["text"],
            "border_color": activeTheme["accent_soft"],
        },
        "danger": {
            "fg_color": activeTheme["danger"],
            "hover_color": activeTheme["primary_hover"],
            "text_color": activeTheme["text"],
            "border_color": activeTheme["danger"],
        },
    }
    config = palette.get(variant, palette["primary"])
    widget.configure(**config)


def createFrame(
    parent,
    *,
    theme: ThemeTokens | None = None,
    fg_color: str | None = None,
    corner_radius: int | None = None,
    border_width: int = 0,
    border_color: str | None = None,
) -> ctk.CTkFrame:
    activeTheme = theme or BASE_THEME
    return ctk.CTkFrame(
        parent,
        fg_color=fg_color or activeTheme["bg"],
        corner_radius=corner_radius or int(activeTheme["radius_md"]),
        border_width=border_width,
        border_color=border_color or activeTheme["border"],
    )


def createScrollableFrame(
    parent,
    *,
    theme: ThemeTokens | None = None,
    fg_color: str | None = None,
    corner_radius: int | None = None,
) -> ctk.CTkScrollableFrame:
    activeTheme = theme or BASE_THEME
    return ctk.CTkScrollableFrame(
        parent,
        fg_color=fg_color or activeTheme["bg"],
        corner_radius=corner_radius or int(activeTheme["radius_md"]),
        border_width=0,
        scrollbar_button_color=activeTheme["surface"],
        scrollbar_button_hover_color=activeTheme["hover"],
    )


def createLabel(
    parent,
    text: str,
    *,
    theme: ThemeTokens | None = None,
    text_color: str | None = None,
    fg_color: str = "transparent",
    font: tuple | None = None,
    anchor: str = "w",
    justify: str = "left",
    wraplength: int = 0,
) -> ctk.CTkLabel:
    activeTheme = theme or BASE_THEME
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=text_color or activeTheme["text"],
        fg_color=fg_color,
        font=font or ("Segoe UI", 12),
        anchor=anchor,
        justify=justify,
        wraplength=wraplength,
    )


def createEntry(
    parent,
    *,
    theme: ThemeTokens | None = None,
    width: int = 240,
    placeholder_text: str = "",
) -> ctk.CTkEntry:
    activeTheme = theme or BASE_THEME
    return ctk.CTkEntry(
        parent,
        width=width,
        height=int(activeTheme["button_height"]),
        corner_radius=int(activeTheme["radius_md"]),
        fg_color=activeTheme["surface"],
        border_color=activeTheme["border"],
        text_color=activeTheme["text"],
        placeholder_text_color=activeTheme["text_muted"],
        placeholder_text=placeholder_text,
        font=("Segoe UI", 13),
    )


def createOptionMenu(
    parent,
    variable,
    values: tuple[str, ...],
    *,
    theme: ThemeTokens | None = None,
    width: int = 180,
) -> ctk.CTkOptionMenu:
    activeTheme = theme or BASE_THEME
    return ctk.CTkOptionMenu(
        parent,
        variable=variable,
        values=list(values),
        width=width,
        height=int(activeTheme["button_height"]),
        corner_radius=int(activeTheme["radius_md"]),
        fg_color=activeTheme["surface"],
        button_color=activeTheme["surface"],
        button_hover_color=activeTheme["hover"],
        dropdown_fg_color=activeTheme["surface"],
        dropdown_hover_color=activeTheme["hover"],
        text_color=activeTheme["text"],
        dropdown_text_color=activeTheme["text"],
        font=("Segoe UI", 13),
    )


def setStatusLabelTone(
    label,
    tone: str,
    theme: ThemeTokens | None = None,
) -> None:
    activeTheme = theme or BASE_THEME
    colorMap = {
        "success": activeTheme["success"],
        "error": activeTheme["danger"],
        "info": activeTheme["accent"],
        "idle": activeTheme["text_secondary"],
        "ready": activeTheme["success"],
    }
    label.configure(text_color=colorMap.get(tone, activeTheme["text_secondary"]))


def clearChildren(widget) -> None:
    for child in widget.winfo_children():
        child.destroy()


def bindRecursive(widget, sequence: str, callback) -> None:
    widget.bind(sequence, callback)
    for child in widget.winfo_children():
        bindRecursive(child, sequence, callback)
