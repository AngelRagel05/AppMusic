from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.youtubePlaylistItemDto import YoutubePlaylistItemDto
from app.presentation.features.comparison.comparisonPaginationState import (
    ComparisonPaginationState,
)
from app.presentation.styles import (
    ActionButton,
    clearChildren,
    createFrame,
    createLabel,
    createOptionMenu,
    createScrollableFrame,
)


PAGE_SIZE_VALUES = ("10", "25", "50", "100")
DEFAULT_PAGE_SIZE = 25
RENDER_BATCH_SIZE = 5


@dataclass
class ComparisonColumnState:
    card: ctk.CTkFrame
    rowsHost: ctk.CTkScrollableFrame
    countLabel: ctk.CTkLabel
    pageLabel: ctk.CTkLabel
    pageSizeVariable: ctk.StringVar
    previousButton: ActionButton
    nextButton: ActionButton
    singularLabel: str
    pluralLabel: str
    emptyTitle: str
    emptyMessage: str
    buildRow: Callable
    pagination: ComparisonPaginationState
    renderToken: int = 0


class ComparisonSplitSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._localSongsColumn = self._buildColumnCard(
            title="Canciones de biblioteca local",
            empty_title="Todavia no hay canciones locales visibles",
            empty_message="Activa una biblioteca local y sincronizala para ver aqui su detalle.",
            singular_label="cancion local",
            plural_label="canciones locales",
            build_row=self._buildLocalSongRow,
        )
        self._localSongsColumn.card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self._youtubePlaylistItemsColumn = self._buildColumnCard(
            title="Items de playlist importados",
            empty_title="Todavia no hay items importados",
            empty_message="Activa una playlist de YouTube e importala para ver aqui su detalle.",
            singular_label="item importado",
            plural_label="items importados",
            build_row=self._buildYoutubePlaylistItemRow,
        )
        self._youtubePlaylistItemsColumn.card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0),
        )

    def showLocalSongs(self, local_songs: list[LocalSongDto]) -> None:
        self._setItems(self._localSongsColumn, local_songs)

    def showYoutubePlaylistItems(
        self,
        youtube_playlist_items: list[YoutubePlaylistItemDto],
    ) -> None:
        self._setItems(self._youtubePlaylistItemsColumn, youtube_playlist_items)

    def _buildColumnCard(
        self,
        *,
        title: str,
        empty_title: str,
        empty_message: str,
        singular_label: str,
        plural_label: str,
        build_row: Callable,
    ) -> ComparisonColumnState:
        card = createFrame(
            self,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header = createFrame(card, theme=self._theme, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        header.grid_columnconfigure(0, weight=1)
        createLabel(
            header,
            title,
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        count_label = createLabel(
            header,
            "0",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        )
        count_label.grid(row=0, column=1, sticky="e")

        controls = createFrame(card, theme=self._theme, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        controls.grid_columnconfigure(0, weight=1)
        page_label = createLabel(
            controls,
            "Sin resultados",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 12, "bold"),
        )
        page_label.grid(row=0, column=0, sticky="w")

        controls_right = createFrame(controls, theme=self._theme, fg_color="transparent")
        controls_right.grid(row=0, column=1, sticky="e")
        createLabel(
            controls_right,
            "Por pagina",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(0, 8))
        page_size_variable = ctk.StringVar(value=str(DEFAULT_PAGE_SIZE))
        page_size_menu = createOptionMenu(
            controls_right,
            page_size_variable,
            values=PAGE_SIZE_VALUES,
            theme=self._theme,
            width=86,
        )
        page_size_menu.pack(side="left", padx=(0, 12))
        previous_button = ActionButton(
            controls_right,
            text="Anterior",
            variant="secondary",
            theme=self._theme,
            height=34,
        )
        previous_button.widget.pack(side="left", padx=(0, 8))
        next_button = ActionButton(
            controls_right,
            text="Siguiente",
            variant="secondary",
            theme=self._theme,
            height=34,
        )
        next_button.widget.pack(side="left")

        rows_host = createScrollableFrame(card, theme=self._theme, fg_color="transparent")
        rows_host.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 18))

        column_state = ComparisonColumnState(
            card=card,
            rowsHost=rows_host,
            countLabel=count_label,
            pageLabel=page_label,
            pageSizeVariable=page_size_variable,
            previousButton=previous_button,
            nextButton=next_button,
            singularLabel=singular_label,
            pluralLabel=plural_label,
            emptyTitle=empty_title,
            emptyMessage=empty_message,
            buildRow=build_row,
            pagination=ComparisonPaginationState(DEFAULT_PAGE_SIZE),
        )
        previous_button.clicked.connect(lambda: self._handlePreviousPageRequested(column_state))
        next_button.clicked.connect(lambda: self._handleNextPageRequested(column_state))
        page_size_menu.configure(
            command=lambda selected_value: self._handlePageSizeChanged(column_state, selected_value)
        )
        self._refreshColumn(column_state)
        return column_state

    def _setItems(self, column_state: ComparisonColumnState, items) -> None:
        column_state.pagination.setItems(items)
        self._refreshColumn(column_state)

    def _handlePageSizeChanged(
        self,
        column_state: ComparisonColumnState,
        selected_value: str,
    ) -> None:
        column_state.pagination.setPageSize(int(selected_value))
        self._refreshColumn(column_state)

    def _handlePreviousPageRequested(self, column_state: ComparisonColumnState) -> None:
        column_state.pagination.previousPage()
        self._refreshColumn(column_state)

    def _handleNextPageRequested(self, column_state: ComparisonColumnState) -> None:
        column_state.pagination.nextPage()
        self._refreshColumn(column_state)

    def _refreshColumn(self, column_state: ComparisonColumnState) -> None:
        column_state.renderToken += 1
        token = column_state.renderToken
        clearChildren(column_state.rowsHost)
        self._refreshColumnLabels(column_state)
        page_items = column_state.pagination.currentItems()
        if not page_items:
            self._showEmptyState(column_state.rowsHost, column_state.emptyTitle, column_state.emptyMessage)
            return

        self._appendRowsChunk(column_state, page_items, 0, token)

    def _refreshColumnLabels(self, column_state: ComparisonColumnState) -> None:
        item_count = column_state.pagination.totalItems
        suffix = column_state.singularLabel if item_count == 1 else column_state.pluralLabel
        column_state.countLabel.configure(text=f"{item_count} {suffix}")

        if item_count == 0:
            column_state.pageLabel.configure(text="Sin resultados")
        else:
            range_start, range_end = column_state.pagination.visibleRange
            column_state.pageLabel.configure(
                text=(
                    f"Pagina {column_state.pagination.currentPage}/{column_state.pagination.totalPages}"
                    f" · {range_start}-{range_end}"
                )
            )

        column_state.previousButton.setEnabled(column_state.pagination.hasPreviousPage)
        column_state.nextButton.setEnabled(column_state.pagination.hasNextPage)

    def _appendRowsChunk(
        self,
        column_state: ComparisonColumnState,
        items,
        start_index: int,
        render_token: int,
    ) -> None:
        if render_token != column_state.renderToken:
            return

        end_index = min(start_index + RENDER_BATCH_SIZE, len(items))
        for item in items[start_index:end_index]:
            column_state.buildRow(column_state.rowsHost, item).pack(fill="x", pady=(0, 12))

        if end_index < len(items):
            column_state.rowsHost.after(
                0,
                lambda: self._appendRowsChunk(column_state, items, end_index, render_token),
            )

    def _buildLocalSongRow(self, parent, local_song: LocalSongDto):
        row = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["surface"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        title = local_song.title or local_song.file_name
        artist = local_song.artist or "Artista desconocido"
        meta_parts = [artist]
        if local_song.album:
            meta_parts.append(local_song.album)
        if local_song.track_number_album > 0:
            meta_parts.append(f"Pista {local_song.track_number_album}")

        createLabel(
            row,
            title,
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
            wraplength=320,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        createLabel(
            row,
            " · ".join(meta_parts),
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 12),
            wraplength=320,
        ).pack(anchor="w", padx=16)
        createLabel(
            row,
            local_song.file_name,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11),
            wraplength=320,
        ).pack(anchor="w", padx=16, pady=(6, 14))
        return row

    def _buildYoutubePlaylistItemRow(self, parent, youtube_playlist_item: YoutubePlaylistItemDto):
        row = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["surface"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        title_row = createFrame(row, theme=self._theme, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(14, 6))
        title_row.grid_columnconfigure(0, weight=1)
        createLabel(
            title_row,
            youtube_playlist_item.raw_title or youtube_playlist_item.normalized_title,
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
            wraplength=280,
        ).grid(row=0, column=0, sticky="w")
        createLabel(
            title_row,
            f"#{youtube_playlist_item.position}",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=1, sticky="e", padx=(12, 0))
        createLabel(
            row,
            youtube_playlist_item.raw_channel_name or youtube_playlist_item.normalized_artist,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 12),
            wraplength=320,
        ).pack(anchor="w", padx=16)
        createLabel(
            row,
            youtube_playlist_item.external_video_id,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11),
            wraplength=320,
        ).pack(anchor="w", padx=16, pady=(6, 14))
        return row

    def _showEmptyState(self, parent, title: str, message: str) -> None:
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["surface"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        createLabel(
            card,
            title,
            theme=self._theme,
            font=("Segoe UI", 16, "bold"),
            wraplength=320,
        ).pack(anchor="w", padx=16, pady=(16, 8))
        createLabel(
            card,
            message,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 12),
            wraplength=320,
        ).pack(anchor="w", padx=16, pady=(0, 16))
        card.pack(fill="x")
