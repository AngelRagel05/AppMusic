from __future__ import annotations

from collections.abc import Callable

from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.ui.comparisonPage.comparisonPage import (
    ComparisonPage,
)
from app.presentation.viewmodels.comparison.libraryComparisonViewModel import (
    ComparisonRecomparisonMode,
    ComparisonSnapshotState,
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
        self._current_recomparison_mode = ComparisonRecomparisonMode.PENDING_ONLY
        self._page.onManualDecisionRequested(self._handleManualDecisionRequested)

    def load(self) -> None:
        active_folder = self._load_active_folder()
        active_playlist = self._load_active_playlist()
        self._page.setActionLabels(
            primary_label=self._page.REFRESH_PRIMARY_ACTION_LABEL,
            secondary_label=self._page.RECOMPARE_PENDING_SECONDARY_ACTION_LABEL,
            tertiary_label=self._page.RECOMPARE_FULL_TERTIARY_ACTION_LABEL,
        )
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
            self._renderCachedSnapshot()
            self._showSnapshotStatusMessage()
            return

        self._page.showComparisonHistory([])
        self._page.showComparisonStatusMessage(
            (
                "No hay snapshot persistido para la biblioteca y playlist activas. "
                "Pulsa \"Recomparar\" para generar el primero."
            ),
            tone="info",
        )

    def refreshComparisonView(self) -> None:
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

        if self._view_model.snapshotState() is ComparisonSnapshotState.RECOMPUTING:
            self._page.showComparisonStatusMessage(
                "Ya hay una recomparacion en curso.",
                tone="info",
            )
            return

        if not self._view_model.refreshPersistedComparison():
            self._page.showComparisonHistory([])
            self._page.showComparisonStatusMessage(
                (
                    "No hay snapshot persistido para la biblioteca y playlist activas. "
                    "Pulsa \"Recomparar\" para generar el primero."
                ),
                tone="info",
            )
            return

        self._renderCachedSnapshot()
        self._showSnapshotStatusMessage()

    def requestPendingRecomparison(self) -> None:
        self._requestRecomparison(ComparisonRecomparisonMode.PENDING_ONLY)

    def requestRecomparison(self) -> None:
        self.requestPendingRecomparison()

    def requestFullRecomparison(self) -> None:
        self._requestRecomparison(ComparisonRecomparisonMode.FULL)

    def _requestRecomparison(self, mode: ComparisonRecomparisonMode) -> None:
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
        if mode is ComparisonRecomparisonMode.FULL:
            if not self._page.confirmFullRecomparisonStart(
                playlist_title=playlist_title,
                folder_name=folder_name,
            ):
                return
            self._page.showLoadingState(
                (
                    f'Recalculando toda la comparacion entre "{playlist_title}" '
                    f'y "{folder_name}"...'
                )
            )
        else:
            if not self._page.confirmManualRecomparisonStart(
                playlist_title=playlist_title,
                folder_name=folder_name,
            ):
                return
            self._page.showLoadingState(
                (
                    f'Recomparando solo pendientes entre "{playlist_title}" '
                    f'y "{folder_name}"...'
                )
            )
        self._current_recomparison_mode = mode
        self._page.after(16, lambda mode=mode: self._startRecomparison(mode))

    def invalidate(self, reason: str | None = None) -> None:
        self._view_model.invalidateComparison(reason)
        active_folder = self._load_active_folder()
        active_playlist = self._load_active_playlist()
        if self._buildMissingContextMessage(active_folder, active_playlist) is None:
            self._showSnapshotStatusMessage()

    def _startRecomparison(self, mode: ComparisonRecomparisonMode) -> None:
        self._view_model.requestRecomparison(
            schedule_on_main_thread=lambda callback: self._page.after(0, callback),
            on_feedback=self._renderComparisonFeedback,
            mode=mode,
        )

    def _renderComparisonFeedback(self, feedback: LibraryComparisonFeedback) -> None:
        self._page.showComparisonStatusMessage(
            feedback.status_message,
            tone=feedback.status_tone,
        )
        self._page.showSnapshotState(
            title=self._buildSnapshotStateTitle(
                feedback.snapshot_state or self._view_model.snapshotState(),
                feedback.recomparison_mode or self._current_recomparison_mode,
            ),
            detail=feedback.invalidation_reason or self._view_model.invalidationReason(),
            tone=self._buildSnapshotStateTone(
                feedback.snapshot_state or self._view_model.snapshotState()
            ),
        )
        self._syncActionLabels(
            feedback.snapshot_state or self._view_model.snapshotState()
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

    def _renderCachedSnapshot(self) -> None:
        comparison_result = self._view_model.load_comparison_result()
        if comparison_result is not None:
            self._page.showComparisonData(
                self._view_model.load_local_songs(),
                comparison_result,
            )
            self._page.showComparisonHistory(
                self._view_model.load_comparison_history()
            )
            return
        self._page.showLocalSongs(self._view_model.load_local_songs())
        self._page.showComparisonHistory([])

    def _showSnapshotStatusMessage(self) -> None:
        self._syncActionLabels(self._view_model.snapshotState())
        snapshot_state = self._view_model.snapshotState()
        invalidation_reason = self._view_model.invalidationReason()
        self._page.showSnapshotState(
            title=self._buildSnapshotStateTitle(
                snapshot_state,
                self._current_recomparison_mode,
            ),
            detail=invalidation_reason,
            tone=self._buildSnapshotStateTone(snapshot_state),
        )
        if snapshot_state is ComparisonSnapshotState.STALE:
            detail_suffix = ""
            if invalidation_reason:
                detail_suffix = f" Motivo: {invalidation_reason}"
            self._page.showComparisonStatusMessage(
                (
                    "Mostrando snapshot persistido desactualizado. "
                    "Pulsa \"Recomparar\" para recalcular con el estado mas reciente."
                    f"{detail_suffix}"
                ),
                tone="info",
            )
            return
        if snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            self._page.showComparisonStatusMessage(
                "Hay una recomparacion en progreso.",
                tone="info",
            )
            return
        self._page.showComparisonStatusMessage(
            "Mostrando snapshot persistido actual.",
            tone="info",
        )

    def _syncActionLabels(
        self,
        snapshot_state: ComparisonSnapshotState,
    ) -> None:
        secondary_label = self._page.RECOMPARE_PENDING_SECONDARY_ACTION_LABEL
        tertiary_label = self._page.RECOMPARE_FULL_TERTIARY_ACTION_LABEL
        if snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            secondary_label = self._page.RECOMPUTING_PENDING_SECONDARY_ACTION_LABEL
            tertiary_label = self._page.RECOMPUTING_FULL_TERTIARY_ACTION_LABEL
        self._page.setActionLabels(
            primary_label=self._page.REFRESH_PRIMARY_ACTION_LABEL,
            secondary_label=secondary_label,
            tertiary_label=tertiary_label,
        )

    def _buildSnapshotStateTitle(
        self,
        snapshot_state: ComparisonSnapshotState,
        recomparison_mode: ComparisonRecomparisonMode,
    ) -> str:
        if snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            if recomparison_mode is ComparisonRecomparisonMode.FULL:
                return "Recalculando todo"
            return "Recomparando pendientes"
        if snapshot_state is ComparisonSnapshotState.STALE:
            return "Snapshot obsoleto"
        return "Snapshot cargado"

    def _buildSnapshotStateTone(
        self,
        snapshot_state: ComparisonSnapshotState,
    ) -> str:
        if snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            return "warning"
        if snapshot_state is ComparisonSnapshotState.STALE:
            return "warning"
        return "success"

    def _handleManualLocalSongLinkRequested(
        self,
        comparison_item: PlaylistComparisonItemResultDto,
        local_song_id: int,
    ) -> bool:
        feedback = self._view_model.updateComparisonItemDecision(
            youtube_playlist_item_id=comparison_item.youtube_playlist_item_id,
            match_status="found",
            local_song_id=local_song_id,
        )
        self._renderComparisonFeedback(feedback)
        return feedback.status_tone != "error"

    def _handleManualDecisionRequested(
        self,
        comparison_item: PlaylistComparisonItemResultDto,
        match_status: str,
        local_song_id: int | None,
    ) -> bool:
        feedback = self._view_model.updateComparisonItemDecision(
            youtube_playlist_item_id=comparison_item.youtube_playlist_item_id,
            match_status=match_status,
            local_song_id=local_song_id,
        )
        self._renderComparisonFeedback(feedback)
        return feedback.status_tone != "error"
