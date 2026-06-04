from __future__ import annotations

from collections.abc import Callable
from threading import Thread

from app.application.dto.importYoutubePlaylistItemsResultDto import (
    ImportYoutubePlaylistItemsResultDto,
)
from app.application.use_cases import ImportYoutubePlaylistItemsUseCase


class ImportYoutubePlaylistItemsWorker:
    def __init__(
        self,
        import_youtube_playlist_items_use_case: ImportYoutubePlaylistItemsUseCase,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
    ) -> None:
        self._import_youtube_playlist_items_use_case = (
            import_youtube_playlist_items_use_case
        )
        self._schedule_on_main_thread = schedule_on_main_thread
        self._thread: Thread | None = None

    def start(
        self,
        on_finished: Callable[[ImportYoutubePlaylistItemsResultDto], None],
        on_failed: Callable[[Exception], None],
    ) -> None:
        def run() -> None:
            try:
                result = self._import_youtube_playlist_items_use_case.execute()
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
