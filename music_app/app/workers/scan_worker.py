from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class ScanWorker(QObject):
    finished = Signal()
    failed = Signal(str)

