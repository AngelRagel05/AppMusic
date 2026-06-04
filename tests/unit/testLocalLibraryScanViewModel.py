from __future__ import annotations

from collections.abc import Callable

from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto
from app.presentation.viewmodels.localLibrary.localLibraryScanViewModel import (
    LocalLibraryScanFeedback,
    LocalLibraryScanViewModel,
)


class ScanLocalFolderUseCaseSpy:
    def __init__(
        self,
        result: ScanLocalFolderResultDto | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.execute_calls = 0

    def execute(self) -> ScanLocalFolderResultDto:
        self.execute_calls += 1
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise AssertionError("El spy necesita resultado o error.")
        return self.result


def runScheduledCallbacks(callbacks: list[Callable[[], None]]) -> None:
    for callback in callbacks:
        callback()


def test_requestScan_emits_start_and_success_feedback() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    view_model = LocalLibraryScanViewModel(
        ScanLocalFolderUseCaseSpy(
            result=ScanLocalFolderResultDto(
                local_folder_id=7,
                local_folder_name="Jazz",
                scanned_file_count=2,
                created_song_count=1,
                existing_song_count=1,
            )
        )
    )

    view_model.requestScan(
        active_folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Jazz",
            display_name="Jazz",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert feedbacks[0] == LocalLibraryScanFeedback(
        status_message='Escaneando la biblioteca "Jazz"...',
        status_tone="info",
        song_count_label="Escaneando...",
        last_action_message=None,
    )
    assert feedbacks[1] == LocalLibraryScanFeedback(
        status_message='Escaneo completado en "Jazz": 2 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas).',
        status_tone="success",
        song_count_label="2 MP3 detectados",
        last_action_message='Escaneo completado en "Jazz": 2 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas).',
    )


def test_requestScan_includes_missing_and_moved_counts_in_success_feedback() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    view_model = LocalLibraryScanViewModel(
        ScanLocalFolderUseCaseSpy(
            result=ScanLocalFolderResultDto(
                local_folder_id=7,
                local_folder_name="Jazz",
                scanned_file_count=3,
                created_song_count=1,
                existing_song_count=1,
                missing_song_count=1,
                moved_song_count=1,
            )
        )
    )

    view_model.requestScan(
        active_folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Jazz",
            display_name="Jazz",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert feedbacks[1] == LocalLibraryScanFeedback(
        status_message='Escaneo completado en "Jazz": 3 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas). Se han marcado 1 ausente, 1 movida detectada.',
        status_tone="success",
        song_count_label="3 MP3 detectados",
        last_action_message='Escaneo completado en "Jazz": 3 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas). Se han marcado 1 ausente, 1 movida detectada.',
    )


def test_requestScan_emits_error_when_no_active_folder_exists() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    view_model = LocalLibraryScanViewModel(ScanLocalFolderUseCaseSpy())

    view_model.requestScan(
        active_folder=None,
        schedule_on_main_thread=lambda _callback: None,
        on_feedback=feedbacks.append,
    )

    assert feedbacks == [
        LocalLibraryScanFeedback(
            status_message="No hay una biblioteca local activa para escanear.",
            status_tone="error",
            song_count_label=None,
            last_action_message=None,
        )
    ]


def test_requestScan_automatic_does_not_emit_feedback_when_scan_is_already_running() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    view_model = LocalLibraryScanViewModel(
        ScanLocalFolderUseCaseSpy(
            result=ScanLocalFolderResultDto(
                local_folder_id=7,
                local_folder_name="Jazz",
                scanned_file_count=2,
                created_song_count=1,
                existing_song_count=1,
            )
        )
    )

    view_model.requestScan(
        active_folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Jazz",
            display_name="Jazz",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    view_model.requestScan(
        active_folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Jazz",
            display_name="Jazz",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
        automatic=True,
    )

    assert feedbacks == [
        LocalLibraryScanFeedback(
            status_message='Escaneando la biblioteca "Jazz"...',
            status_tone="info",
            song_count_label="Escaneando...",
            last_action_message=None,
        )
    ]
