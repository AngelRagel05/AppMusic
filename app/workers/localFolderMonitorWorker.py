from __future__ import annotations

from collections.abc import Callable
from threading import Event, Thread
from typing import Protocol


class LocalFolderSnapshotReaderPort(Protocol):
    def readSnapshotSignature(self, folderPath: str) -> tuple[tuple[str, int, int], ...]:
        ...


class LocalFolderMonitorWorker:
    def __init__(
        self,
        snapshot_reader: LocalFolderSnapshotReaderPort,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
        polling_interval_seconds: float = 2.0,
    ) -> None:
        self._snapshot_reader = snapshot_reader
        self._schedule_on_main_thread = schedule_on_main_thread
        self._polling_interval_seconds = polling_interval_seconds
        self._thread: Thread | None = None
        self._stop_event: Event | None = None
        self._folder_path: str | None = None

    def watch(
        self,
        folder_path: str | None,
        on_folder_changed: Callable[[], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        normalizedFolderPath = (folder_path or "").strip()
        if not normalizedFolderPath:
            self.stop()
            return

        if (
            self._thread is not None
            and self._thread.is_alive()
            and self._folder_path == normalizedFolderPath
        ):
            return

        self.stop()
        self._folder_path = normalizedFolderPath
        stopEvent = Event()
        self._stop_event = stopEvent

        def run() -> None:
            try:
                previousSnapshot = self._snapshot_reader.readSnapshotSignature(normalizedFolderPath)
                while not stopEvent.wait(self._polling_interval_seconds):
                    currentSnapshot = self._snapshot_reader.readSnapshotSignature(normalizedFolderPath)
                    if currentSnapshot == previousSnapshot:
                        continue

                    previousSnapshot = currentSnapshot
                    self._schedule_on_main_thread(on_folder_changed)
            except Exception as error:
                self._schedule_on_main_thread(lambda error=error: on_failed(error))

        self._thread = Thread(
            target=run,
            name="localFolderMonitorWorker",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=max(self._polling_interval_seconds, 0.1) + 0.1)

        self._thread = None
        self._stop_event = None
        self._folder_path = None
