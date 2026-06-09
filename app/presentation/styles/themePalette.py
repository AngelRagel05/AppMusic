from __future__ import annotations

from typing import TypeAlias

ThemeTokens: TypeAlias = dict[str, str | int]

BASE_THEME: ThemeTokens = {
    "bg": "#121212",
    "sidebar": "#1B1B1B",
    "panel": "#202020",
    "surface": "#242424",
    "hover": "#2D2D2D",
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
    "radius_sm": 12,
    "radius_md": 16,
    "radius_lg": 18,
    "sidebar_width": 224,
    "page_padding": 40,
    "title_size": 30,
    "subtitle_size": 14,
    "label_size": 12,
    "value_size": 22,
    "button_height": 42,
    "sidebar_button_height": 36,
}

PAGE_THEME_OVERRIDES: dict[str, ThemeTokens] = {
    "comparison": {
        "panel": "#1C1C1C",
        "surface": "#191919",
        "hover": "#252525",
        "border": "#2C2C2C",
        "accent_soft": "#223043",
        "radius_sm": 4,
        "radius_md": 6,
        "radius_lg": 6,
        "page_padding": 16,
        "title_size": 22,
        "subtitle_size": 13,
        "label_size": 11,
        "value_size": 17,
        "button_height": 30,
    },
    "overview": {},
    "localLibrary": {},
    "youtubePlaylists": {},
    "ignoredTerms": {},
}


def mergeTheme(baseTheme: ThemeTokens, overrides: ThemeTokens | None = None) -> ThemeTokens:
    merged = dict(baseTheme)
    if overrides:
        merged.update(overrides)
    return merged


def getPageTheme(pageName: str, overrides: ThemeTokens | None = None) -> ThemeTokens:
    pageTheme = PAGE_THEME_OVERRIDES.get(pageName, {})
    return mergeTheme(mergeTheme(BASE_THEME, pageTheme), overrides)
