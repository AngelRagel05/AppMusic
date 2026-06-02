from __future__ import annotations

from typing import TypeAlias

ThemeTokens: TypeAlias = dict[str, str]

BASE_THEME: ThemeTokens = {
    "bg": "#121212",
    "panel": "#1E1E1E",
    "surface": "#262626",
    "surface_alt": "#303030",
    "border": "#343434",
    "text": "#FFFFFF",
    "text_secondary": "#D0D0D0",
    "text_muted": "#8A8A8A",
    "primary": "#D64545",
    "primary_hover": "#C13A3A",
    "accent": "#5B8DEF",
    "accent_soft": "#263246",
    "success": "#3DA37C",
    "warning": "#C7A252",
    "danger": "#D64545",
}

PAGE_THEME_OVERRIDES: dict[str, ThemeTokens] = {
    "overview": {},
    "libraries": {
        "accent": "#4D9F70",
        "accent_soft": "#20392C",
    },
    "playlists": {
        "accent": "#D86C3F",
        "accent_soft": "#40261C",
    },
    "filters": {
        "accent": "#8B7CF6",
        "accent_soft": "#2D2949",
    },
}


def mergeTheme(baseTheme: ThemeTokens, overrides: ThemeTokens | None = None) -> ThemeTokens:
    merged = dict(baseTheme)
    if overrides:
        merged.update(overrides)
    return merged


def getPageTheme(pageName: str, overrides: ThemeTokens | None = None) -> ThemeTokens:
    pageTheme = PAGE_THEME_OVERRIDES.get(pageName, {})
    return mergeTheme(mergeTheme(BASE_THEME, pageTheme), overrides)
