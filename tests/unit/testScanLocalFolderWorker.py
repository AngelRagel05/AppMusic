from __future__ import annotations

from collections.abc import Callable

from app.application.dto.scanLocalFolderProgressDto import ScanLocalFolderProgressDto
from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto
from app.workers.scanLocalFolderWorker import ScanLocalFolderWorker


class ScanLocalFolderUseCaseSpy:
    def __init__(
        self,
        result: ScanLocalFolderResultDto | None = None,
        error: Exception | None = None,
        progress_events: list[ScanLocalFolderProgressDto] | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.progress_events = progress_events or []

    def execute(self, on_progress=None) -> ScanLocalFolderResultDto:
        if on_progress is not None:
            for progress in self.progress_events:
                on_progress(progress)
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise AssertionError("El spy necesita resultado o error.")
        return self.result


def runScheduledCallbacks(callbacks: list[Callable[[], None]]) -> None:
    for callback in callbacks:
        callback()


def test_start_schedules_success_callback_on_main_thread() -> None:
    scheduled_callbacks: list[Callable[[], None]] = []
    received_progress: list[ScanLocalFolderProgressDto] = []
    received_results: list[ScanLocalFolderResultDto] = []
    received_errors: list[Exception] = []
    worker = ScanLocalFolderWorker(
        ScanLocalFolderUseCaseSpy(
            progress_events=[ScanLocalFolderProgressDto(processed_song_count=1, total_song_count=2)],
            result=ScanLocalFolderResultDto(
                local_folder_id=7,
                local_folder_name="Jazz",
                scanned_file_count=2,
                created_song_count=1,
                existing_song_count=1,
            )
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
    )

    worker.start(
        on_progress=received_progress.append,
        on_finished=received_results.append,
        on_failed=received_errors.append,
    )
    worker._thread.join(timeout=1)
    runScheduledCallbacks(scheduled_callbacks)

    assert received_progress == [ScanLocalFolderProgressDto(processed_song_count=1, total_song_count=2)]
    assert len(received_results) == 1
    assert received_results[0].local_folder_name == "Jazz"
    assert received_errors == []


def test_start_schedules_error_callback_on_main_thread() -> None:
    scheduled_callbacks: list[Callable[[], None]] = []
    received_progress: list[ScanLocalFolderProgressDto] = []
    received_results: list[ScanLocalFolderResultDto] = []
    received_errors: list[Exception] = []
    worker = ScanLocalFolderWorker(
        ScanLocalFolderUseCaseSpy(error=ValueError("No hay una biblioteca local activa para escanear.")),
        schedule_on_main_thread=scheduled_callbacks.append,
    )

    worker.start(
        on_progress=received_progress.append,
        on_finished=received_results.append,
        on_failed=received_errors.append,
    )
    worker._thread.join(timeout=1)
    runScheduledCallbacks(scheduled_callbacks)

    assert received_progress == []
    assert received_results == []
    assert len(received_errors) == 1
    assert str(received_errors[0]) == "No hay una biblioteca local activa para escanear."
