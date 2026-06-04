from __future__ import annotations

from app.presentation.features.comparison.ui.comparisonPage.comparisonPage import (
    ComparisonPage,
)
from app.presentation.viewmodels.comparison.libraryComparisonViewModel import (
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
        local_songs, youtube_playlist_items = self._view_model.refreshState()
        self._page.showLocalSongs(local_songs)
        self._page.showYoutubePlaylistItems(youtube_playlist_items)
