from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QTableWidget

from app.presentation.styles import loadQss


def configureDataTable(table: QTableWidget) -> None:
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(False)
    table.horizontalHeader().setHighlightSections(False)
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    table.setMinimumHeight(260)
    table.setStyleSheet(loadQss(Path(__file__).with_suffix(".qss")))
