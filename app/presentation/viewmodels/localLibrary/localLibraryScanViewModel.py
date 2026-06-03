from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.scanLocalFolderResultDto import ScanLocalFolderResultDto
from app.application.use_cases import ScanLocalFolderUseCase
from app.workers import ScanLocalFolderWorker


@dataclass(frozen=True, slots=True)
class LocalLibraryScanFeedback:
    status_message: str
    status_tone: str
    song_count_label: str | None = None
    last_action_message: str | None = None


class LocalLibraryScanViewModel:
    def __init__(self, scan_local_folder_use_case: ScanLocalFolderUseCase) -> None:
        self._scan_local_folder_use_case = scan_local_folder_use_case
        self._scan_in_progress = False

    def requestScan(
        self,
        active_folder: LocalFolderDto | None,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
        on_feedback: Callable[[LocalLibraryScanFeedback], None],
    ) -> None:
        if self._scan_in_progress:
            on_feedback(
                LocalLibraryScanFeedback(
                    status_message="Ya hay un escaneo de biblioteca en curso.",
                    status_tone="info",
                )
            )
            return

        if active_folder is None:
            on_feedback(
                LocalLibraryScanFeedback(
                    status_message="No hay una biblioteca local activa para escanear.",
                    status_tone="error",
                )
            )
            return

        self._scan_in_progress = True
        on_feedback(
            LocalLibraryScanFeedback(
                status_message=f'Escaneando la biblioteca "{active_folder.display_name}"...',
                status_tone="info",
                song_count_label="Escaneando...",
            )
        )
        scan_worker = ScanLocalFolderWorker(
            self._scan_local_folder_use_case,
            schedule_on_main_thread=schedule_on_main_thread,
        )
        scan_worker.start(
            on_finished=lambda result: self._handleCompleted(result, on_feedback),
            on_failed=lambda error: self._handleFailed(error, on_feedback),
        )

    def _handleCompleted(
        self,
        result: ScanLocalFolderResultDto,
        on_feedback: Callable[[LocalLibraryScanFeedback], None],
    ) -> None:
        self._scan_in_progress = False
        registeredSongCount = result.created_song_count + result.existing_song_count
        message = (
            f'Escaneo completado en "{result.local_folder_name}": '
            f"{result.scanned_file_count} MP3 detectados, "
            f"{registeredSongCount} canciones registradas "
            f"({result.created_song_count} nuevas y {result.existing_song_count} ya registradas)."
        )
        on_feedback(
            LocalLibraryScanFeedback(
                status_message=message,
                status_tone="success",
                song_count_label=self._formatDetectedMp3Count(result.scanned_file_count),
                last_action_message=message,
            )
        )

    def _handleFailed(
        self,
        error: Exception,
        on_feedback: Callable[[LocalLibraryScanFeedback], None],
    ) -> None:
        self._scan_in_progress = False
        on_feedback(
            LocalLibraryScanFeedback(
                status_message=str(error),
                status_tone="error",
                song_count_label="Sin escanear",
            )
        )

    def _formatDetectedMp3Count(self, song_count: int) -> str:
        suffix = "MP3 detectado" if song_count == 1 else "MP3 detectados"
        return f"{song_count} {suffix}"
