from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.workers import LoadLibraryComparisonWorker


@dataclass(frozen=True, slots=True)
class LibraryComparisonFeedback:
    status_message: str
    status_tone: str
    local_songs: list[LocalSongDto] | None = None
    comparison_result: PlaylistComparisonResultDto | None = None
    last_action_message: str | None = None


class LibraryComparisonViewModel:
    def __init__(
        self,
        load_library_comparison: Callable[
            [],
            tuple[list[LocalSongDto], PlaylistComparisonResultDto],
        ],
        load_persisted_comparison: Callable[
            [],
            tuple[list[LocalSongDto], PlaylistComparisonResultDto] | None,
        ],
    ) -> None:
        self._load_library_comparison = load_library_comparison
        self._load_persisted_comparison = load_persisted_comparison
        self._local_songs_cache: list[LocalSongDto] = []
        self._comparison_result_cache: PlaylistComparisonResultDto | None = None
        self._comparison_in_progress = False
        self._comparison_is_stale = True

    def requestComparison(
        self,
        schedule_on_main_thread: Callable[[Callable[[], None]], None],
        on_feedback: Callable[[LibraryComparisonFeedback], None],
    ) -> None:
        if self._comparison_in_progress:
            on_feedback(
                LibraryComparisonFeedback(
                    status_message="Ya hay una comparacion en curso.",
                    status_tone="info",
                )
            )
            return

        self._comparison_in_progress = True
        on_feedback(
            LibraryComparisonFeedback(
                status_message="Comparando biblioteca local contra playlist activa...",
                status_tone="info",
            )
        )
        comparison_worker = LoadLibraryComparisonWorker(
            self._load_library_comparison,
            schedule_on_main_thread=schedule_on_main_thread,
        )
        comparison_worker.start(
            on_finished=lambda local_songs, comparison_result: self._handleCompleted(
                local_songs,
                comparison_result,
                on_feedback,
            ),
            on_failed=lambda error: self._handleFailed(error, on_feedback),
        )

    def load_local_songs(self) -> list[LocalSongDto]:
        return list(self._local_songs_cache)

    def load_comparison_result(self) -> PlaylistComparisonResultDto | None:
        return self._comparison_result_cache

    def hasCachedComparison(self) -> bool:
        return self._comparison_result_cache is not None

    def restorePersistedComparison(self) -> bool:
        if self._comparison_result_cache is not None:
            return True

        persisted_snapshot = self._load_persisted_comparison()
        if persisted_snapshot is None:
            return False

        local_songs, comparison_result = persisted_snapshot
        self._local_songs_cache = list(local_songs)
        self._comparison_result_cache = comparison_result
        self._comparison_is_stale = False
        return True

    def isComparisonStale(self) -> bool:
        return self._comparison_is_stale

    def invalidateComparison(self) -> None:
        self._comparison_is_stale = True

    def _handleCompleted(
        self,
        local_songs: list[LocalSongDto],
        comparison_result: PlaylistComparisonResultDto,
        on_feedback: Callable[[LibraryComparisonFeedback], None],
    ) -> None:
        self._comparison_in_progress = False
        self._local_songs_cache = list(local_songs)
        self._comparison_result_cache = comparison_result
        self._comparison_is_stale = False
        summary = comparison_result.summary
        message = (
            "Comparacion completada: "
            f"{summary.found_count} encontradas, "
            f"{summary.possible_match_count} posibles coincidencias y "
            f"{summary.missing_count} faltan."
        )
        on_feedback(
            LibraryComparisonFeedback(
                status_message=message,
                status_tone="success",
                local_songs=list(local_songs),
                comparison_result=comparison_result,
                last_action_message=message,
            )
        )

    def _handleFailed(
        self,
        error: Exception,
        on_feedback: Callable[[LibraryComparisonFeedback], None],
    ) -> None:
        self._comparison_in_progress = False
        on_feedback(
            LibraryComparisonFeedback(
                status_message=str(error),
                status_tone="error",
            )
        )
