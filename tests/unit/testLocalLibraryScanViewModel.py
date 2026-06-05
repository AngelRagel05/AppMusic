from __future__ import annotations

from collections.abc import Callable

from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.scanLocalFolderProgressDto import ScanLocalFolderProgressDto
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
        progress_events: list[ScanLocalFolderProgressDto] | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.execute_calls = 0
        self.progress_events = progress_events or []

    def execute(self, on_progress=None) -> ScanLocalFolderResultDto:
        self.execute_calls += 1
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


def test_requestScan_emits_start_and_success_feedback() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    use_case = ScanLocalFolderUseCaseSpy(
        progress_events=[
            ScanLocalFolderProgressDto(processed_song_count=0, total_song_count=2),
            ScanLocalFolderProgressDto(processed_song_count=1, total_song_count=2),
        ],
        result=ScanLocalFolderResultDto(
            local_folder_id=7,
            local_folder_name="Jazz",
            scanned_file_count=2,
            created_song_count=1,
            updated_song_count=1,
            existing_song_count=1,
        ),
    )
    view_model = LocalLibraryScanViewModel(
        use_case.execute
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
        status_message="Escaneando biblioteca...",
        status_tone="info",
        song_count_label="0/2 canciones",
        last_action_message=None,
    )
    assert feedbacks[2] == LocalLibraryScanFeedback(
        status_message="Escaneando biblioteca...",
        status_tone="info",
        song_count_label="1/2 canciones",
        last_action_message=None,
    )
    assert feedbacks[3] == LocalLibraryScanFeedback(
        status_message='Escaneo completado en "Jazz": 2 MP3 detectados, 1 anadidas, 1 actualizadas y 0 eliminadas.',
        status_tone="success",
        song_count_label="2 MP3 detectados",
        last_action_message='Escaneo completado en "Jazz": 2 MP3 detectados, 1 anadidas, 1 actualizadas y 0 eliminadas.',
    )


def test_requestScan_includes_missing_and_moved_counts_in_success_feedback() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    use_case = ScanLocalFolderUseCaseSpy(
        result=ScanLocalFolderResultDto(
            local_folder_id=7,
            local_folder_name="Jazz",
            scanned_file_count=3,
            created_song_count=1,
            updated_song_count=1,
            existing_song_count=0,
            missing_song_count=1,
            moved_song_count=1,
        )
    )
    view_model = LocalLibraryScanViewModel(
        use_case.execute
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
        status_message='Escaneo completado en "Jazz": 3 MP3 detectados, 1 anadidas, 1 actualizadas y 1 eliminadas. Ademas, se han detectado 1 movimiento detectado.',
        status_tone="success",
        song_count_label="3 MP3 detectados",
        last_action_message='Escaneo completado en "Jazz": 3 MP3 detectados, 1 anadidas, 1 actualizadas y 1 eliminadas. Ademas, se han detectado 1 movimiento detectado.',
    )


def test_requestScan_emits_error_when_no_active_folder_exists() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    view_model = LocalLibraryScanViewModel(ScanLocalFolderUseCaseSpy().execute)

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
    use_case = ScanLocalFolderUseCaseSpy(
        result=ScanLocalFolderResultDto(
            local_folder_id=7,
            local_folder_name="Jazz",
            scanned_file_count=2,
            created_song_count=1,
            updated_song_count=0,
            existing_song_count=1,
        )
    )
    view_model = LocalLibraryScanViewModel(
        use_case.execute
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


def test_requestScan_emits_clear_error_when_folder_does_not_exist() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    use_case = ScanLocalFolderUseCaseSpy(
        error=ValueError(
            'La carpeta local "Jazz" no existe o ya no esta disponible: C:\\Music\\Missing.'
        )
    )
    view_model = LocalLibraryScanViewModel(
        use_case.execute
    )

    view_model.requestScan(
        active_folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Missing",
            display_name="Jazz",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert feedbacks[1] == LocalLibraryScanFeedback(
        status_message='La carpeta local "Jazz" no existe o ya no esta disponible: C:\\Music\\Missing.',
        status_tone="error",
        song_count_label="Sin escanear",
        last_action_message=None,
    )


def test_requestScan_emits_clear_error_when_folder_cannot_be_read() -> None:
    feedbacks: list[LocalLibraryScanFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    use_case = ScanLocalFolderUseCaseSpy(
        error=ValueError(
            'No se puede leer la carpeta local "Jazz": C:\\Music\\Restricted. Revisa los permisos e intentalo de nuevo.'
        )
    )
    view_model = LocalLibraryScanViewModel(
        use_case.execute
    )

    view_model.requestScan(
        active_folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Restricted",
            display_name="Jazz",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert feedbacks[1] == LocalLibraryScanFeedback(
        status_message='No se puede leer la carpeta local "Jazz": C:\\Music\\Restricted. Revisa los permisos e intentalo de nuevo.',
        status_tone="error",
        song_count_label="Sin escanear",
        last_action_message=None,
    )
