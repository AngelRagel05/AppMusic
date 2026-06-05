from __future__ import annotations

from collections.abc import Callable
from threading import Thread

from app.application.dto.importYoutubePlaylistItemsResultDto import (
    ImportYoutubePlaylistItemsResultDto,
)


class ImportYoutubePlaylistItemsWorker:
    def __init__(
        self,
        execute_import_youtube_playlist_items: Callable[
            [],
            ImportYoutubePlaylistItemsResultDto,
        ],
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
    ) -> None:
        self._execute_import_youtube_playlist_items = execute_import_youtube_playlist_items
        self._schedule_on_main_thread = schedule_on_main_thread
        self._thread: Thread | None = None

    def start(
        self,
        on_finished: Callable[[ImportYoutubePlaylistItemsResultDto], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        def run() -> None:
            try:
                result = self._execute_import_youtube_playlist_items()
            except Exception as error:
                self._schedule_on_main_thread(lambda error=error: on_failed(error))
                return

            self._schedule_on_main_thread(lambda result=result: on_finished(result))

        self._thread = Thread(
            target=run,
            name="importYoutubePlaylistItemsWorker",
            daemon=True,
        )
        self._thread.start()
