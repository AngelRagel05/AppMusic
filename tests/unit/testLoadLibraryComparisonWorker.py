from __future__ import annotations

from collections.abc import Callable

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.workers.loadLibraryComparisonWorker import LoadLibraryComparisonWorker
from datetime import UTC, datetime


class StubListActiveLocalSongsUseCase:
    def __init__(self, result: list[LocalSongDto] | None = None, error: Exception | None = None) -> None:
        self.result = result or []
        self.error = error

    def execute(self) -> list[LocalSongDto]:
        if self.error is not None:
            raise self.error
        return list(self.result)


class StubCompareUseCase:
    def __init__(
        self,
        result: PlaylistComparisonResultDto | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error

    def execute(self) -> PlaylistComparisonResultDto:
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise AssertionError("El spy necesita resultado o error.")
        return self.result


def loadLibraryComparison(
    list_active_local_songs_use_case: StubListActiveLocalSongsUseCase,
    compare_use_case: StubCompareUseCase,
    comparison_history: list[PlaylistComparisonHistoryEntryDto],
) -> tuple[
    list[LocalSongDto],
    PlaylistComparisonResultDto,
    list[PlaylistComparisonHistoryEntryDto],
]:
    return (
        list_active_local_songs_use_case.execute(),
        compare_use_case.execute(),
        list(comparison_history),
    )


def runScheduledCallbacks(callbacks: list[Callable[[], None]]) -> None:
    for callback in callbacks:
        callback()


def test_start_schedules_success_callback_on_main_thread() -> None:
    scheduled_callbacks: list[Callable[[], None]] = []
    received_payloads: list[
        tuple[
            list[LocalSongDto],
            PlaylistComparisonResultDto,
            list[PlaylistComparisonHistoryEntryDto],
        ]
    ] = []
    received_errors: list[Exception] = []
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=7,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            album="Album One",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.0,
        )
    ]
    comparison_result = PlaylistComparisonResultDto(
        summary=PlaylistComparisonSummaryDto(
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        ),
        items=[],
    )
    comparison_history = [
        PlaylistComparisonHistoryEntryDto(
            comparison_id=3,
            compared_at=datetime(2026, 6, 8, 12, 0, tzinfo=UTC),
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        )
    ]
    list_use_case = StubListActiveLocalSongsUseCase(local_songs)
    compare_use_case = StubCompareUseCase(comparison_result)
    worker = LoadLibraryComparisonWorker(
        lambda: loadLibraryComparison(list_use_case, compare_use_case, comparison_history),
        schedule_on_main_thread=scheduled_callbacks.append,
    )

    worker.start(
        on_finished=lambda loaded_local_songs, loaded_comparison_result, loaded_comparison_history: received_payloads.append(
            (loaded_local_songs, loaded_comparison_result, loaded_comparison_history)
        ),
        on_failed=received_errors.append,
    )
    worker._thread.join(timeout=1)
    runScheduledCallbacks(scheduled_callbacks)

    assert received_errors == []
    assert received_payloads == [(local_songs, comparison_result, comparison_history)]


def test_start_schedules_error_callback_on_main_thread() -> None:
    scheduled_callbacks: list[Callable[[], None]] = []
    received_payloads: list[
        tuple[
            list[LocalSongDto],
            PlaylistComparisonResultDto,
            list[PlaylistComparisonHistoryEntryDto],
        ]
    ] = []
    received_errors: list[Exception] = []
    list_use_case = StubListActiveLocalSongsUseCase(
        error=ValueError("No hay una biblioteca local activa para comparar.")
    )
    compare_use_case = StubCompareUseCase(
        PlaylistComparisonResultDto(
            summary=PlaylistComparisonSummaryDto(
                found_count=0,
                missing_count=0,
                possible_match_count=0,
                total_compared=0,
            ),
            items=[],
        )
    )
    worker = LoadLibraryComparisonWorker(
        lambda: loadLibraryComparison(list_use_case, compare_use_case, []),
        schedule_on_main_thread=scheduled_callbacks.append,
    )

    worker.start(
        on_finished=lambda loaded_local_songs, loaded_comparison_result, loaded_comparison_history: received_payloads.append(
            (loaded_local_songs, loaded_comparison_result, loaded_comparison_history)
        ),
        on_failed=received_errors.append,
    )
    worker._thread.join(timeout=1)
    runScheduledCallbacks(scheduled_callbacks)

    assert received_payloads == []
    assert len(received_errors) == 1
    assert str(received_errors[0]) == "No hay una biblioteca local activa para comparar."
