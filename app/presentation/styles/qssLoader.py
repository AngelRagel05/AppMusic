from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget

from app.presentation.styles.theme import THEME_TOKENS


def loadQss(qssPath: str | Path) -> str:
    content = Path(qssPath).read_text(encoding="utf-8")
    for token, value in THEME_TOKENS.items():
        content = content.replace(f"{{{{{token}}}}}", value)
    return content


def applyComponentQss(widget: QWidget, qssPath: str | Path) -> None:
    widget.setStyleSheet(loadQss(qssPath))
