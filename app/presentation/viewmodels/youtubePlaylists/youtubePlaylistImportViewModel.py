from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.application.use_cases import ImportYoutubePlaylistItemsUseCase
from app.workers import ImportYoutubePlaylistItemsWorker


@dataclass(frozen=True, slots=True)
class YoutubePlaylistImportFeedback:
    status_message: str
    status_tone: str
    last_action_message: str | None = None


class YoutubePlaylistImportViewModel:
    def __init__(
        self,
        import_youtube_playlist_items_use_case: ImportYoutubePlaylistItemsUseCase,
    ) -> None:
        self._import_youtube_playlist_items_use_case = (
            import_youtube_playlist_items_use_case
        )
        self._import_in_progress = False

    def requestImport(
        self,
        active_playlist: YoutubePlaylistDto | None,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
        on_feedback: Callable[[YoutubePlaylistImportFeedback], None],
    ) -> None:
        if self._import_in_progress:
            on_feedback(
                YoutubePlaylistImportFeedback(
                    status_message="Ya hay una importacion de playlist en curso.",
                    status_tone="info",
                )
            )
            return

        if active_playlist is None:
            on_feedback(
                YoutubePlaylistImportFeedback(
                    status_message="No hay una playlist principal activa para importar.",
                    status_tone="error",
                )
            )
            return

        self._import_in_progress = True
        on_feedback(
            YoutubePlaylistImportFeedback(
                status_message=(
                    f'Importando items de la playlist "{active_playlist.title}"...'
                ),
                status_tone="info",
            )
        )
        import_worker = ImportYoutubePlaylistItemsWorker(
            self._import_youtube_playlist_items_use_case,
            schedule_on_main_thread=schedule_on_main_thread,
        )
        import_worker.start(
            on_finished=lambda result: self._handleCompleted(result, on_feedback),
            on_failed=lambda error: self._handleFailed(error, on_feedback),
        )

    def _handleCompleted(
        self,
        result,
        on_feedback: Callable[[YoutubePlaylistImportFeedback], None],
    ) -> None:
        self._import_in_progress = False
        message = (
            f'Importacion completada en "{result.playlist_title}": '
            f"{result.imported_item_count} items importados."
        )
        on_feedback(
            YoutubePlaylistImportFeedback(
                status_message=message,
                status_tone="success",
                last_action_message=message,
            )
        )

    def _handleFailed(
        self,
        error: Exception,
        on_feedback: Callable[[YoutubePlaylistImportFeedback], None],
    ) -> None:
        self._import_in_progress = False
        on_feedback(
            YoutubePlaylistImportFeedback(
                status_message=str(error),
                status_tone="error",
            )
        )
