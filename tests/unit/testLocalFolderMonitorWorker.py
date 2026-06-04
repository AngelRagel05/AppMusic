from __future__ import annotations

from collections.abc import Callable
from time import sleep

from app.workers.localFolderMonitorWorker import LocalFolderMonitorWorker


class LocalFolderSnapshotReaderSpy:
    def __init__(self, snapshots: list[tuple[tuple[str, int, int], ...]]) -> None:
        self._snapshots = snapshots
        self._call_count = 0

    def readSnapshotSignature(self, _folderPath: str) -> tuple[tuple[str, int, int], ...]:
        index = min(self._call_count, len(self._snapshots) - 1)
        self._call_count += 1
        return self._snapshots[index]


def runScheduledCallbacks(callbacks: list[Callable[[], None]]) -> None:
    for callback in callbacks:
        callback()


def test_watch_schedules_callback_when_snapshot_changes() -> None:
    scheduledCallbacks: list[Callable[[], None]] = []
    detectedChanges: list[str] = []
    receivedErrors: list[Exception] = []
    worker = LocalFolderMonitorWorker(
        snapshot_reader=LocalFolderSnapshotReaderSpy(
            [
                (("C:/Music/song.mp3", 100, 1),),
                (("C:/Music/song.mp3", 100, 1),),
                (("C:/Music/song.mp3", 110, 2),),
            ]
        ),
        schedule_on_main_thread=scheduledCallbacks.append,
        polling_interval_seconds=0.01,
    )

    worker.watch(
        folder_path=r"C:\Music",
        on_folder_changed=lambda: detectedChanges.append("changed"),
        on_failed=receivedErrors.append,
    )
    sleep(0.05)
    worker.stop()
    runScheduledCallbacks(scheduledCallbacks)

    assert detectedChanges == ["changed"]
    assert receivedErrors == []


def test_watch_restarts_monitor_when_folder_path_changes() -> None:
    scheduledCallbacks: list[Callable[[], None]] = []
    worker = LocalFolderMonitorWorker(
        snapshot_reader=LocalFolderSnapshotReaderSpy([()]),
        schedule_on_main_thread=scheduledCallbacks.append,
        polling_interval_seconds=0.01,
    )

    worker.watch(
        folder_path=r"C:\Music\Jazz",
        on_folder_changed=lambda: None,
        on_failed=lambda _error: None,
    )
    firstThread = worker._thread
    worker.watch(
        folder_path=r"C:\Music\Rock",
        on_folder_changed=lambda: None,
        on_failed=lambda _error: None,
    )
    secondThread = worker._thread
    worker.stop()

    assert firstThread is not None
    assert secondThread is not None
    assert firstThread is not secondThread
