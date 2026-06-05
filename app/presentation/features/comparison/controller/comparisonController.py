from __future__ import annotations

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
    ) -> None:
        self._page = page
        self._view_model = view_model

    def load(self) -> None:
        if not self._view_model.hasCachedComparison():
            self._view_model.restorePersistedComparison()

        if self._view_model.hasCachedComparison():
            comparison_result = self._view_model.load_comparison_result()
            if comparison_result is not None:
                self._page.showComparisonData(
                    self._view_model.load_local_songs(),
                    comparison_result,
                )
            else:
                self._page.showLocalSongs(self._view_model.load_local_songs())
            if self._view_model.isComparisonStale():
                self._page.showComparisonStatusMessage(
                    "Los resultados visibles pueden estar desactualizados. Pulsa \"Refrescar comparacion\" para recalcularlos y actualizar la base de datos.",
                    tone="info",
                )
            return

        self._page.showComparisonStatusMessage(
            "Pulsa \"Refrescar comparacion\" para calcular la comparacion y guardar el resultado actualizado.",
            tone="info",
        )

    def requestComparison(self) -> None:
        if not self._page.confirmManualComparisonStart():
            return
        self._page.showLoadingState(
            "Recalculando resultados y actualizando la base de datos..."
        )
        self._page.after(16, self._startComparison)

    def invalidate(self) -> None:
        self._view_model.invalidateComparison()

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
        if (
            feedback.local_songs is not None
            and feedback.comparison_result is not None
        ):
            self._page.showComparisonData(
                feedback.local_songs,
                feedback.comparison_result,
            )
            return
        if feedback.local_songs is not None:
            self._page.showLocalSongs(feedback.local_songs)
        if feedback.comparison_result is not None:
            self._page.showComparisonResults(feedback.comparison_result)
