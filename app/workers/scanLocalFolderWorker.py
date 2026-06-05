from __future__ import annotations

from collections.abc import Callable
from threading import Thread

from app.application.dto.scanLocalFolderProgressDto import ScanLocalFolderProgressDto
from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto


class ScanLocalFolderWorker:
    def __init__(
        self,
        execute_scan_local_folder: Callable[
            [Callable[[ScanLocalFolderProgressDto], None]],
            ScanLocalFolderResultDto,
        ],
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
    ) -> None:
        self._execute_scan_local_folder = execute_scan_local_folder
        self._schedule_on_main_thread = schedule_on_main_thread
        self._thread: Thread | None = None

    def start(
        self,
        on_progress: Callable[[ScanLocalFolderProgressDto], None],
        on_finished: Callable[[ScanLocalFolderResultDto], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        def run() -> None:
            try:
                result = self._execute_scan_local_folder(
                    lambda progress: self._schedule_on_main_thread(
                        lambda progress=progress: on_progress(progress)
                    )
                )
            except Exception as error:
                self._schedule_on_main_thread(lambda error=error: on_failed(error))
                return

            self._schedule_on_main_thread(lambda result=result: on_finished(result))

        self._thread = Thread(
            target=run,
            name="scanLocalFolderWorker",
            daemon=True,
        )
        self._thread.start()
