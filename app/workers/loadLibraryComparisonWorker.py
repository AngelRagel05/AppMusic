from __future__ import annotations

from collections.abc import Callable
from threading import Thread

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto


class LoadLibraryComparisonWorker:
    def __init__(
        self,
        load_library_comparison: Callable[
            [],
            tuple[list[LocalSongDto], PlaylistComparisonResultDto],
        ],
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
    ) -> None:
        self._load_library_comparison = load_library_comparison
        self._schedule_on_main_thread = schedule_on_main_thread
        self._thread: Thread | None = None

    def start(
        self,
        on_finished: Callable[[list[LocalSongDto], PlaylistComparisonResultDto], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        def run() -> None:
            try:
                local_songs, comparison_result = self._load_library_comparison()
            except Exception as error:
                self._schedule_on_main_thread(lambda error=error: on_failed(error))
                return

            self._schedule_on_main_thread(
                lambda local_songs=local_songs, comparison_result=comparison_result: on_finished(
                    local_songs,
                    comparison_result,
                )
            )

        self._thread = Thread(
            target=run,
            name="loadLibraryComparisonWorker",
            daemon=True,
        )
        self._thread.start()
