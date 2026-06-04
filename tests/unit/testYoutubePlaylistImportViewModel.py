from __future__ import annotations

from collections.abc import Callable

from app.application.dto.importYoutubePlaylistItemsResultDto import (
    ImportYoutubePlaylistItemsResultDto,
)
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.viewmodels.youtubePlaylists.youtubePlaylistImportViewModel import (
    YoutubePlaylistImportFeedback,
    YoutubePlaylistImportViewModel,
)


class ImportYoutubePlaylistItemsUseCaseSpy:
    def __init__(
        self,
        result: ImportYoutubePlaylistItemsResultDto | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.execute_calls = 0

    def execute(self) -> ImportYoutubePlaylistItemsResultDto:
        self.execute_calls += 1
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise AssertionError("El spy necesita resultado o error.")
        return self.result


def runScheduledCallbacks(callbacks: list[Callable[[], None]]) -> None:
    for callback in callbacks:
        callback()


def test_requestImport_emits_start_and_success_feedback() -> None:
    feedbacks: list[YoutubePlaylistImportFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    view_model = YoutubePlaylistImportViewModel(
        ImportYoutubePlaylistItemsUseCaseSpy(
            result=ImportYoutubePlaylistItemsResultDto(
                youtube_playlist_id=9,
                playlist_title="Favoritas",
                imported_item_count=42,
            )
        )
    )

    view_model.requestImport(
        active_playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert feedbacks == [
        YoutubePlaylistImportFeedback(
            status_message='Importando items de la playlist "Favoritas"...',
            status_tone="info",
            last_action_message=None,
        ),
        YoutubePlaylistImportFeedback(
            status_message='Importacion completada en "Favoritas": 42 items importados.',
            status_tone="success",
            last_action_message='Importacion completada en "Favoritas": 42 items importados.',
        ),
    ]


def test_requestImport_emits_error_when_no_active_playlist_exists() -> None:
    feedbacks: list[YoutubePlaylistImportFeedback] = []
    view_model = YoutubePlaylistImportViewModel(ImportYoutubePlaylistItemsUseCaseSpy())

    view_model.requestImport(
        active_playlist=None,
        schedule_on_main_thread=lambda _callback: None,
        on_feedback=feedbacks.append,
    )

    assert feedbacks == [
        YoutubePlaylistImportFeedback(
            status_message="No hay una playlist principal activa para importar.",
            status_tone="error",
            last_action_message=None,
        )
    ]


def test_requestImport_emits_import_error_feedback() -> None:
    feedbacks: list[YoutubePlaylistImportFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []
    view_model = YoutubePlaylistImportViewModel(
        ImportYoutubePlaylistItemsUseCaseSpy(
            error=ValueError("La playlist no puede leerse o no esta disponible.")
        )
    )

    view_model.requestImport(
        active_playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert feedbacks[1] == YoutubePlaylistImportFeedback(
        status_message="La playlist no puede leerse o no esta disponible.",
        status_tone="error",
        last_action_message=None,
    )
