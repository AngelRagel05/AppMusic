from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.updatePlaylistComparisonResultInputDto import (
    UpdatePlaylistComparisonResultInputDto,
)
from app.shared.constants.comparison import ComparisonStatus
from app.workers import LoadLibraryComparisonWorker


@dataclass(frozen=True, slots=True)
class LibraryComparisonFeedback:
    status_message: str
    status_tone: str
    snapshot_state: "ComparisonSnapshotState | None" = None
    invalidation_reason: str | None = None
    recomparison_mode: "ComparisonRecomparisonMode | None" = None
    local_songs: list[LocalSongDto] | None = None
    comparison_result: PlaylistComparisonResultDto | None = None
    comparison_history: list[PlaylistComparisonHistoryEntryDto] | None = None
    last_action_message: str | None = None


class ComparisonSnapshotState(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    RECOMPUTING = "recomputing"


class ComparisonRecomparisonMode(str, Enum):
    PENDING_ONLY = "pending_only"
    FULL = "full"


class LibraryComparisonViewModel:
    def __init__(
        self,
        recompare_pending_library_comparison: Callable[
            [],
            tuple[
                list[LocalSongDto],
                PlaylistComparisonResultDto,
                list[PlaylistComparisonHistoryEntryDto],
            ],
        ],
        recompare_full_library_comparison: Callable[
            [],
            tuple[
                list[LocalSongDto],
                PlaylistComparisonResultDto,
                list[PlaylistComparisonHistoryEntryDto],
            ],
        ],
        load_persisted_comparison: Callable[
            [],
            tuple[
                list[LocalSongDto],
                PlaylistComparisonResultDto,
                list[PlaylistComparisonHistoryEntryDto],
            ]
            | None,
        ],
        update_playlist_comparison_result: Callable[
            [UpdatePlaylistComparisonResultInputDto],
            tuple[
                list[LocalSongDto],
                PlaylistComparisonResultDto,
                list[PlaylistComparisonHistoryEntryDto],
            ]
            | None,
        ]
        | None = None,
    ) -> None:
        self._recompare_pending_library_comparison = recompare_pending_library_comparison
        self._recompare_full_library_comparison = recompare_full_library_comparison
        self._load_persisted_comparison = load_persisted_comparison
        self._update_playlist_comparison_result = update_playlist_comparison_result
        self._local_songs_cache: list[LocalSongDto] = []
        self._comparison_result_cache: PlaylistComparisonResultDto | None = None
        self._comparison_history_cache: list[PlaylistComparisonHistoryEntryDto] = []
        self._snapshot_state = ComparisonSnapshotState.FRESH
        self._previous_snapshot_state = ComparisonSnapshotState.FRESH
        self._invalidation_reason: str | None = None

    def requestRecomparison(
        self,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
        on_feedback: Callable[[LibraryComparisonFeedback], None],
        *,
        mode: ComparisonRecomparisonMode = ComparisonRecomparisonMode.PENDING_ONLY,
    ) -> None:
        if self._snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            on_feedback(
                LibraryComparisonFeedback(
                    status_message="Ya hay una recomparacion en curso.",
                    status_tone="info",
                    snapshot_state=self._snapshot_state,
                    invalidation_reason=self._invalidation_reason,
                )
            )
            return

        self._previous_snapshot_state = self._snapshot_state
        self._snapshot_state = ComparisonSnapshotState.RECOMPUTING
        self._invalidation_reason = None
        status_message = "Recomparando coincidencias pendientes con el estado actual..."
        if mode is ComparisonRecomparisonMode.FULL:
            status_message = "Recalculando toda la comparacion desde cero..."
        on_feedback(
            LibraryComparisonFeedback(
                status_message=status_message,
                status_tone="info",
                snapshot_state=self._snapshot_state,
                recomparison_mode=mode,
            )
        )
        comparison_worker = LoadLibraryComparisonWorker(
            (
                self._recompare_full_library_comparison
                if mode is ComparisonRecomparisonMode.FULL
                else self._recompare_pending_library_comparison
            ),
            schedule_on_main_thread=schedule_on_main_thread,
        )
        comparison_worker.start(
            on_finished=lambda local_songs, comparison_result, comparison_history: self._handleCompleted(
                local_songs,
                comparison_result,
                comparison_history,
                on_feedback,
                mode=mode,
            ),
            on_failed=lambda error: self._handleFailed(error, on_feedback),
        )

    def load_local_songs(self) -> list[LocalSongDto]:
        return list(self._local_songs_cache)

    def load_comparison_result(self) -> PlaylistComparisonResultDto | None:
        return self._comparison_result_cache

    def load_comparison_history(self) -> list[PlaylistComparisonHistoryEntryDto]:
        return list(self._comparison_history_cache)

    def hasCachedComparison(self) -> bool:
        return self._comparison_result_cache is not None

    def restorePersistedComparison(self) -> bool:
        if self._comparison_result_cache is not None:
            return True
        return self.refreshPersistedComparison()

    def refreshPersistedComparison(self) -> bool:
        if self._snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            return self._comparison_result_cache is not None

        persisted_snapshot = self._load_persisted_comparison()
        if persisted_snapshot is None:
            return False

        local_songs, comparison_result, comparison_history = persisted_snapshot
        self._local_songs_cache = list(local_songs)
        self._comparison_result_cache = comparison_result
        self._comparison_history_cache = list(comparison_history)
        if self._snapshot_state is not ComparisonSnapshotState.STALE:
            self._snapshot_state = ComparisonSnapshotState.FRESH
        return True

    def isComparisonStale(self) -> bool:
        return self._snapshot_state is ComparisonSnapshotState.STALE

    def snapshotState(self) -> ComparisonSnapshotState:
        return self._snapshot_state

    def invalidationReason(self) -> str | None:
        return self._invalidation_reason

    def invalidateComparison(self, reason: str | None = None) -> None:
        if self._snapshot_state is ComparisonSnapshotState.RECOMPUTING:
            return
        self._snapshot_state = ComparisonSnapshotState.STALE
        self._invalidation_reason = reason

    def updateComparisonItemDecision(
        self,
        *,
        youtube_playlist_item_id: int,
        match_status: str,
        local_song_id: int | None,
    ) -> LibraryComparisonFeedback:
        if self._comparison_result_cache is None:
            return LibraryComparisonFeedback(
                status_message="No hay una comparacion cargada para editar.",
                status_tone="error",
            )
        if self._comparison_result_cache.playlist_comparison_id is None:
            return LibraryComparisonFeedback(
                status_message="La comparacion actual no tiene un snapshot persistido editable.",
                status_tone="error",
            )
        if self._update_playlist_comparison_result is None:
            return LibraryComparisonFeedback(
                status_message="La edicion manual de resultados no esta disponible.",
                status_tone="error",
            )

        try:
            updated_snapshot = self._update_playlist_comparison_result(
                UpdatePlaylistComparisonResultInputDto(
                    playlist_comparison_id=self._comparison_result_cache.playlist_comparison_id,
                    youtube_playlist_item_id=youtube_playlist_item_id,
                    match_status=match_status,
                    local_song_id=local_song_id,
                )
            )
        except Exception as error:
            return LibraryComparisonFeedback(
                status_message=str(error),
                status_tone="error",
            )

        if updated_snapshot is None:
            return LibraryComparisonFeedback(
                status_message="No se pudo recargar el snapshot actualizado.",
                status_tone="error",
            )

        local_songs, comparison_result, comparison_history = updated_snapshot
        self._local_songs_cache = list(local_songs)
        self._comparison_result_cache = comparison_result
        self._comparison_history_cache = list(comparison_history)
        self._snapshot_state = ComparisonSnapshotState.FRESH
        self._invalidation_reason = None
        message = self._buildManualDecisionMessage(
            match_status=match_status,
            local_song_id=local_song_id,
        )
        return LibraryComparisonFeedback(
            status_message=message,
            status_tone="success",
            snapshot_state=self._snapshot_state,
            invalidation_reason=self._invalidation_reason,
            local_songs=list(local_songs),
            comparison_result=comparison_result,
            comparison_history=list(comparison_history),
            last_action_message=message,
        )

    def _buildManualDecisionMessage(
        self,
        *,
        match_status: str,
        local_song_id: int | None,
    ) -> str:
        normalized_status = ComparisonStatus(match_status)
        if normalized_status is ComparisonStatus.MISSING:
            return "Resultado marcado manualmente como faltante."
        if normalized_status is ComparisonStatus.POSSIBLE_MATCH:
            if local_song_id is None:
                return "Resultado marcado manualmente como posible coincidencia."
            return "Resultado guardado como posible coincidencia con cancion local enlazada."
        return "Resultado marcado manualmente como encontrada con cancion local enlazada."

    def _handleCompleted(
        self,
        local_songs: list[LocalSongDto],
        comparison_result: PlaylistComparisonResultDto,
        comparison_history: list[PlaylistComparisonHistoryEntryDto],
        on_feedback: Callable[[LibraryComparisonFeedback], None],
        *,
        mode: ComparisonRecomparisonMode,
    ) -> None:
        self._local_songs_cache = list(local_songs)
        self._comparison_result_cache = comparison_result
        self._comparison_history_cache = list(comparison_history)
        self._snapshot_state = ComparisonSnapshotState.FRESH
        self._invalidation_reason = None
        summary = comparison_result.summary
        prefix = "Recomparacion de pendientes completada"
        if mode is ComparisonRecomparisonMode.FULL:
            prefix = "Recomparacion completa finalizada"
        message = (
            f"{prefix}: "
            f"{summary.found_count} encontradas, "
            f"{summary.possible_match_count} posibles coincidencias y "
            f"{summary.missing_count} faltan."
        )
        on_feedback(
            LibraryComparisonFeedback(
                status_message=message,
                status_tone="success",
                snapshot_state=self._snapshot_state,
                recomparison_mode=mode,
                local_songs=list(local_songs),
                comparison_result=comparison_result,
                comparison_history=list(comparison_history),
                last_action_message=message,
            )
        )

    def _handleFailed(
        self,
        error: Exception,
        on_feedback: Callable[[LibraryComparisonFeedback], None],
    ) -> None:
        self._snapshot_state = self._previous_snapshot_state
        on_feedback(
            LibraryComparisonFeedback(
                status_message=str(error),
                status_tone="error",
                snapshot_state=self._snapshot_state,
                invalidation_reason=self._invalidation_reason,
            )
        )
