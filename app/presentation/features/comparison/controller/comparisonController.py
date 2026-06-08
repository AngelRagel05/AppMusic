from __future__ import annotations

from collections.abc import Callable

from app.presentation.features.comparison.ui.comparisonPage.comparisonPage import (
    ComparisonPage,
)
from app.presentation.viewmodels.comparison.libraryComparisonViewModel import (
    LibraryComparisonFeedback,
    LibraryComparisonViewModel,
)


class ComparisonController:
    def __init__(
        self,
        page: ComparisonPage,
        view_model: LibraryComparisonViewModel,
        load_active_folder: Callable[[], object | None],
        load_active_playlist: Callable[[], object | None],
    ) -> None:
        self._page = page
        self._view_model = view_model
        self._load_active_folder = load_active_folder
        self._load_active_playlist = load_active_playlist

    def load(self) -> None:
        active_folder = self._load_active_folder()
        active_playlist = self._load_active_playlist()
        self._page.setPrimaryActionLabel(self._page.DEFAULT_PRIMARY_ACTION_LABEL)
        missing_context_message = self._buildMissingContextMessage(
            active_folder,
            active_playlist,
        )
        if missing_context_message is not None:
            self._page.showComparisonHistory([])
            self._page.showComparisonStatusMessage(missing_context_message, tone="info")
            return

        if not self._view_model.hasCachedComparison():
            self._view_model.restorePersistedComparison()

        if self._view_model.hasCachedComparison():
            comparison_result = self._view_model.load_comparison_result()
            if comparison_result is not None:
                self._page.showComparisonData(
                    self._view_model.load_local_songs(),
                    comparison_result,
                )
                self._page.showComparisonHistory(
                    self._view_model.load_comparison_history()
                )
            else:
                self._page.showLocalSongs(self._view_model.load_local_songs())
                self._page.showComparisonHistory([])
            if self._view_model.isComparisonStale():
                self._showRerunPrompt()
            return

        self._page.showComparisonHistory([])
        self._page.showComparisonStatusMessage(
            "Pulsa \"Refrescar comparacion\" para calcular la comparacion y guardar el resultado actualizado.",
            tone="info",
        )

    def requestComparison(self) -> None:
        active_folder = self._load_active_folder()
        active_playlist = self._load_active_playlist()
        missing_context_message = self._buildMissingContextMessage(
            active_folder,
            active_playlist,
        )
        if missing_context_message is not None:
            self._page.showComparisonHistory([])
            self._page.showComparisonStatusMessage(missing_context_message, tone="error")
            return

        playlist_title = getattr(active_playlist, "title", "Playlist activa")
        folder_name = getattr(active_folder, "display_name", "Biblioteca activa")
        if not self._page.confirmManualComparisonStart(
            playlist_title=playlist_title,
            folder_name=folder_name,
        ):
            return
        self._page.showLoadingState(
            (
                f'Recalculando la comparacion entre "{playlist_title}" '
                f'y "{folder_name}"...'
            )
        )
        self._page.after(16, self._startComparison)

    def invalidate(self) -> None:
        self._view_model.invalidateComparison()
        active_folder = self._load_active_folder()
        active_playlist = self._load_active_playlist()
        if self._buildMissingContextMessage(active_folder, active_playlist) is None:
            self._showRerunPrompt()

    def _startComparison(self) -> None:
        self._view_model.requestComparison(
            schedule_on_main_thread=lambda callback: self._page.after(0, callback),
            on_feedback=self._renderComparisonFeedback,
        )

    def _renderComparisonFeedback(self, feedback: LibraryComparisonFeedback) -> None:
        self._page.showComparisonStatusMessage(
            feedback.status_message,
            tone=feedback.status_tone,
        )
        if feedback.status_tone == "error" or feedback.comparison_result is not None:
            self._page.hideLoadingState()
        if feedback.comparison_result is not None:
            self._page.setPrimaryActionLabel(self._page.DEFAULT_PRIMARY_ACTION_LABEL)
        if (
            feedback.local_songs is not None
            and feedback.comparison_result is not None
        ):
            self._page.showComparisonData(
                feedback.local_songs,
                feedback.comparison_result,
            )
            self._page.showComparisonHistory(feedback.comparison_history or [])
            return
        if feedback.local_songs is not None:
            self._page.showLocalSongs(feedback.local_songs)
        if feedback.comparison_history is not None:
            self._page.showComparisonHistory(feedback.comparison_history)
        if feedback.comparison_result is not None:
            self._page.showComparisonResults(feedback.comparison_result)

    def _buildMissingContextMessage(
        self,
        active_folder,
        active_playlist,
    ) -> str | None:
        if active_playlist is None and active_folder is None:
            return (
                "Activa una playlist de YouTube y una biblioteca local para ejecutar la comparacion."
            )
        if active_playlist is None:
            return "Activa una playlist de YouTube para ejecutar la comparacion."
        if active_folder is None:
            return "Activa una biblioteca local para ejecutar la comparacion."
        return None

    def _showRerunPrompt(self) -> None:
        self._page.setPrimaryActionLabel(self._page.RERUN_PRIMARY_ACTION_LABEL)
        self._page.showComparisonStatusMessage(
            (
                "La biblioteca o la playlist activas han cambiado. "
                "Pulsa \"Volver a comparar\" para recalcular los resultados con el estado mas reciente."
            ),
            tone="info",
        )
