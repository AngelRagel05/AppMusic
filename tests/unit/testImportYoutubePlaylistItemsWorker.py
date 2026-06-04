from __future__ import annotations

from collections.abc import Callable

from app.application.dto.importYoutubePlaylistItemsResultDto import (
    ImportYoutubePlaylistItemsResultDto,
)
from app.workers.importYoutubePlaylistItemsWorker import (
    ImportYoutubePlaylistItemsWorker,
)


class ImportYoutubePlaylistItemsUseCaseSpy:
    def __init__(
        self,
        result: ImportYoutubePlaylistItemsResultDto | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error

    def execute(self) -> ImportYoutubePlaylistItemsResultDto:
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
    received_results: list[ImportYoutubePlaylistItemsResultDto] = []
    received_errors: list[Exception] = []
    worker = ImportYoutubePlaylistItemsWorker(
        ImportYoutubePlaylistItemsUseCaseSpy(
            result=ImportYoutubePlaylistItemsResultDto(
                youtube_playlist_id=9,
                playlist_title="Favoritas",
                imported_item_count=42,
                created_item_count=3,
                updated_item_count=2,
                existing_item_count=37,
                removed_item_count=1,
            )
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
    )

    worker.start(
        on_finished=received_results.append,
        on_failed=received_errors.append,
    )
    worker._thread.join(timeout=1)
    runScheduledCallbacks(scheduled_callbacks)

    assert received_errors == []
    assert received_results == [
        ImportYoutubePlaylistItemsResultDto(
            youtube_playlist_id=9,
            playlist_title="Favoritas",
            imported_item_count=42,
            created_item_count=3,
            updated_item_count=2,
            existing_item_count=37,
            removed_item_count=1,
        )
    ]


def test_start_schedules_error_callback_on_main_thread() -> None:
    scheduled_callbacks: list[Callable[[], None]] = []
    received_results: list[ImportYoutubePlaylistItemsResultDto] = []
    received_errors: list[Exception] = []
    worker = ImportYoutubePlaylistItemsWorker(
        ImportYoutubePlaylistItemsUseCaseSpy(
            error=ValueError("No hay una playlist principal activa para importar.")
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
    )

    worker.start(
        on_finished=received_results.append,
        on_failed=received_errors.append,
    )
    worker._thread.join(timeout=1)
    runScheduledCallbacks(scheduled_callbacks)

    assert received_results == []
    assert len(received_errors) == 1
    assert str(received_errors[0]) == "No hay una playlist principal activa para importar."
