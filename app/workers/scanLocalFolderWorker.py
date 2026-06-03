from __future__ import annotations

from collections.abc import Callable
from threading import Thread

from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto
from app.application.use_cases import ScanLocalFolderUseCase


class ScanLocalFolderWorker:
    def __init__(
        self,
        scan_local_folder_use_case: ScanLocalFolderUseCase,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
    ) -> None:
        self._scan_local_folder_use_case = scan_local_folder_use_case
        self._schedule_on_main_thread = schedule_on_main_thread
        self._thread: Thread | None = None

    def start(
        self,
        on_finished: Callable[[ScanLocalFolderResultDto], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        def run() -> None:
            try:
                result = self._scan_local_folder_use_case.execute()
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
