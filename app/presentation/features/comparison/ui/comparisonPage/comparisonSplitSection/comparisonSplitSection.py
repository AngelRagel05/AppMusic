from __future__ import annotations

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonLinkedLocalSongSummary import (
    buildComparisonLinkedLocalSongSummary,
)
from app.presentation.features.comparison.comparisonResultDetailViewData import (
    buildComparisonResultDetailViewData,
)
from app.presentation.features.comparison.comparisonTableRowViewData import (
    buildComparisonTableRowViewData,
)
from app.presentation.features.comparison.ui.comparisonPage.comparisonResultDetailDialog.comparisonResultDetailDialog import (
    ComparisonResultDetailDialog,
)
from app.presentation.features.comparison.comparisonSearch import (
    filterComparisonItemsByQuery,
)
from app.presentation.features.comparison.comparisonPaginationState import (
    ComparisonPaginationState,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    ALL_COMPARISON_FILTER,
    filterComparisonItemsByStatus,
)
from app.presentation.styles import (
    bindRecursive,
    clearChildren,
    createFrame,
    createLabel,
    createOptionMenu,
    createScrollableFrame,
)
from app.shared.constants.comparison import ComparisonStatus


PAGE_SIZE_VALUES = ("25", "50", "75", "100")
DEFAULT_PAGE_SIZE = 25
RENDER_BATCH_SIZE = 25
FAST_MOUSE_WHEEL_UNITS = 4
SCROLL_INCREMENT_PIXELS = 36
TABLE_COLUMNS: tuple[tuple[str, int, str], ...] = (
    ("Estado", 1, "w"),
    ("Titulo playlist", 3, "w"),
    ("Artista", 2, "w"),
    ("Coincidencia local", 3, "w"),
    ("Score", 1, "center"),
    ("Revision", 2, "w"),
)


class ComparisonSplitSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        self._allLocalSongs: list[LocalSongDto] = []
        self._localSongsById: dict[int, LocalSongDto] = {}
        self._allComparisonItems: list[PlaylistComparisonItemResultDto] = []
        self._selectedComparisonFilter = ALL_COMPARISON_FILTER
        self._searchQuery = ""
        self._selectedItemKey: int | None = None
        self._detailDialog: ComparisonResultDetailDialog | None = None
        self._renderToken = 0
        self._pagination = ComparisonPaginationState(DEFAULT_PAGE_SIZE)
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._buildLayout()

    def showLocalSongs(self, local_songs: list[LocalSongDto]) -> None:
        self._allLocalSongs = list(local_songs)
        self._localSongsById = {local_song.id: local_song for local_song in self._allLocalSongs}
        self._refreshResultsTable()

    def showComparisonData(
        self,
        local_songs: list[LocalSongDto],
        comparison_items: list[PlaylistComparisonItemResultDto],
    ) -> None:
        self._allLocalSongs = list(local_songs)
        self._localSongsById = {local_song.id: local_song for local_song in self._allLocalSongs}
        self._allComparisonItems = list(comparison_items)
        self._refreshResultsTable()

    def showComparisonResults(
        self,
        comparison_items: list[PlaylistComparisonItemResultDto],
    ) -> None:
        self._allComparisonItems = list(comparison_items)
        self._refreshResultsTable()

    def setComparisonFilter(self, selected_filter: str) -> None:
        self._selectedComparisonFilter = selected_filter
        self._refreshResultsTable()

    def setSearchQuery(self, query: str) -> None:
        self._searchQuery = query
        self._refreshResultsTable()

    def _buildLayout(self) -> None:
        card = createFrame(
            self,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        card.grid_rowconfigure(2, weight=1)
        card.grid_rowconfigure(3, weight=0)
        card.grid_columnconfigure(0, weight=1)
        card.grid(row=0, column=0, sticky="nsew")
        self._card = card

        header = createFrame(card, theme=self._theme, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
        header.grid_columnconfigure(0, weight=1)
        createLabel(
            header,
            "Tabla de resultados de comparacion",
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self._countLabel = createLabel(
            header,
            "0 resultados",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12),
        )
        self._countLabel.grid(row=0, column=1, sticky="e")

        controls = createFrame(card, theme=self._theme, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
        controls.grid_columnconfigure(0, weight=1)
        self._pageLabel = createLabel(
            controls,
            "Sin resultados",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
        )
        self._pageLabel.grid(row=0, column=0, sticky="w")

        controls_right = createFrame(controls, theme=self._theme, fg_color="transparent")
        controls_right.grid(row=0, column=1, sticky="e")
        createLabel(
            controls_right,
            "Por pag.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(0, 8))
        self._pageSizeVariable = ctk.StringVar(value=str(DEFAULT_PAGE_SIZE))
        page_size_menu = createOptionMenu(
            controls_right,
            self._pageSizeVariable,
            values=PAGE_SIZE_VALUES,
            theme=self._theme,
            width=70,
        )
        page_size_menu.configure(font=("Segoe UI", 11))
        page_size_menu.pack(side="left", padx=(0, 8))
        self._previousButton = ctk.CTkButton(
            controls_right,
            text="< Anterior",
            height=28,
            width=84,
            corner_radius=int(self._theme["radius_md"]),
            fg_color=self._theme["surface"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            border_width=0,
            font=("Segoe UI", 11),
            command=self._handlePreviousPageRequested,
        )
        self._previousButton.pack(side="left", padx=(0, 6))
        self._nextButton = ctk.CTkButton(
            controls_right,
            text="Siguiente >",
            height=28,
            width=84,
            corner_radius=int(self._theme["radius_md"]),
            fg_color=self._theme["surface"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            border_width=0,
            font=("Segoe UI", 11),
            command=self._handleNextPageRequested,
        )
        self._nextButton.pack(side="left")

        page_size_menu.configure(
            command=self._handlePageSizeChanged
        )
        table = createFrame(
            card,
            theme=self._theme,
            fg_color=self._theme["surface"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        table.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(1, weight=1)

        self._tableHeader = createFrame(table, theme=self._theme, fg_color=self._theme["panel"])
        self._tableHeader.grid(row=0, column=0, sticky="ew")
        self._configureTableColumns(self._tableHeader)
        for column_index, (title, _weight, anchor) in enumerate(TABLE_COLUMNS):
            createLabel(
                self._tableHeader,
                title,
                theme=self._theme,
                text_color=self._theme["text_muted"],
                font=("Segoe UI", 11, "bold"),
                anchor=anchor,
                justify="center" if anchor == "center" else "left",
            ).grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=(10 if column_index == 0 else 6, 10 if column_index == len(TABLE_COLUMNS) - 1 else 6),
                pady=(8, 8),
            )

        self._rowsHost = createScrollableFrame(table, theme=self._theme, fg_color="transparent")
        self._rowsHost.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._configureFastScroll(self._rowsHost)

        self._detailCard = createFrame(
            card,
            theme=self._theme,
            fg_color=self._theme["surface"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        self._detailCard.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._detailCard.grid_columnconfigure(0, weight=1)
        createLabel(
            self._detailCard,
            "Detalle del resultado",
            theme=self._theme,
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        self._detailSummaryLabel = createLabel(
            self._detailCard,
            "Selecciona una fila para revisar la coincidencia local y el motivo detectado.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=920,
        )
        self._detailSummaryLabel.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 4))
        self._detailLinkedSongLabel = createLabel(
            self._detailCard,
            "",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=920,
        )
        self._detailLinkedSongLabel.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 4))
        self._detailReasonLabel = createLabel(
            self._detailCard,
            "",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11),
            wraplength=920,
        )
        self._detailReasonLabel.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 8))
        self._openDetailButton = ctk.CTkButton(
            self._detailCard,
            text="Abrir detalle",
            height=30,
            width=132,
            corner_radius=int(self._theme["radius_md"]),
            fg_color=self._theme["accent"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text"],
            border_width=0,
            font=("Segoe UI", 11, "bold"),
            state="disabled",
            command=self._openSelectedResultDetail,
        )
        self._openDetailButton.grid(row=4, column=0, sticky="e", padx=10, pady=(0, 10))

        self._refreshResultsTable()

    def _refreshResultsTable(self) -> None:
        filtered_comparison_items = filterComparisonItemsByStatus(
            self._allComparisonItems,
            self._selectedComparisonFilter,
        )
        filtered_comparison_items = filterComparisonItemsByQuery(
            filtered_comparison_items,
            self._searchQuery,
        )
        self._pagination.setItems(filtered_comparison_items)
        visible_ids = {item.youtube_playlist_item_id for item in filtered_comparison_items}
        if self._selectedItemKey not in visible_ids:
            self._selectedItemKey = None
        self._renderToken += 1
        token = self._renderToken
        self._scrollRowsToTop()
        clearChildren(self._rowsHost)
        self._refreshTableLabels()
        page_items = self._pagination.currentItems()
        if not page_items:
            self._showEmptyState()
            self._showEmptyDetail()
            return

        if self._selectedItemKey is None:
            self._selectedItemKey = page_items[0].youtube_playlist_item_id
        self._appendRowsChunk(page_items, 0, token)
        self._refreshDetailFromSelection(page_items)

    def _handlePageSizeChanged(self, selected_value: str) -> None:
        self._pagination.setPageSize(int(selected_value))
        self._refreshResultsTable()

    def _handlePreviousPageRequested(self) -> None:
        self._pagination.previousPage()
        self._refreshResultsTable()

    def _handleNextPageRequested(self) -> None:
        self._pagination.nextPage()
        self._refreshResultsTable()

    def _refreshTableLabels(self) -> None:
        item_count = self._pagination.totalItems
        suffix = "resultado" if item_count == 1 else "resultados"
        self._countLabel.configure(text=f"{item_count} {suffix}")

        if item_count == 0:
            self._pageLabel.configure(text="Sin resultados")
        else:
            range_start, range_end = self._pagination.visibleRange
            self._pageLabel.configure(
                text=(
                    f"Pág. {self._pagination.currentPage}/{self._pagination.totalPages}"
                    f"  {range_start}-{range_end}"
                )
            )

        self._previousButton.configure(
            state="normal" if self._pagination.hasPreviousPage else "disabled"
        )
        self._nextButton.configure(
            state="normal" if self._pagination.hasNextPage else "disabled"
        )

    def _appendRowsChunk(
        self,
        items,
        start_index: int,
        render_token: int,
    ) -> None:
        if render_token != self._renderToken:
            return

        end_index = min(start_index + RENDER_BATCH_SIZE, len(items))
        for item in items[start_index:end_index]:
            row_key = item.youtube_playlist_item_id
            row = self._buildComparisonResultRow(
                self._rowsHost,
                item,
                self._selectedItemKey == row_key,
            )
            row._comparison_row_key = row_key
            row._comparison_status = getattr(item, "comparison_status", None)
            row._comparison_item = item
            self._bindRowInteractivity(row, row_key)
            row.pack(fill="x")

        if end_index < len(items):
            self._rowsHost.after(
                0,
                lambda: self._appendRowsChunk(items, end_index, render_token),
            )

    def _buildComparisonResultRow(
        self,
        parent,
        comparison_item: PlaylistComparisonItemResultDto,
        is_selected: bool,
    ):
        row_data = buildComparisonTableRowViewData(comparison_item)
        row = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._rowColor(is_selected, comparison_item.comparison_status),
            corner_radius=int(self._theme["radius_sm"]),
            border_width=self._rowBorderWidth(comparison_item.comparison_status),
            border_color=self._rowBorderColor(comparison_item.comparison_status),
        )
        self._configureTableColumns(row)
        row.grid_propagate(False)

        row_values = (
            (row_data.status_label, self._availabilityColor(comparison_item.comparison_status), "bold"),
            (row_data.playlist_title, self._theme["text"], "normal"),
            (row_data.playlist_artist, self._theme["text_secondary"], "normal"),
            (row_data.local_match, self._theme["text"], "normal"),
            (row_data.score_label, self._theme["text_secondary"], "normal"),
            (row_data.review_note, self._theme["text_secondary"], "normal"),
        )
        for column_index, (value, color, weight) in enumerate(row_values):
            anchor = TABLE_COLUMNS[column_index][2]
            createLabel(
                row,
                value,
                theme=self._theme,
                text_color=color,
                font=("Segoe UI", 11, weight),
                anchor=anchor,
                justify="center" if anchor == "center" else "left",
            ).grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=(10 if column_index == 0 else 6, 10 if column_index == len(row_values) - 1 else 6),
                pady=(7, 7),
            )
        self._buildRowSeparator(row).grid(row=1, column=0, columnspan=len(TABLE_COLUMNS), sticky="ew")
        return row

    def _availabilityColor(self, status: ComparisonStatus) -> str:
        return {
            ComparisonStatus.FOUND: self._theme["success"],
            ComparisonStatus.MISSING: self._theme["danger"],
            ComparisonStatus.POSSIBLE_MATCH: self._theme["accent"],
        }[status]

    def _configureFastScroll(self, rows_host: ctk.CTkScrollableFrame) -> None:
        canvas = getattr(rows_host, "_parent_canvas", None)
        if canvas is None:
            return
        canvas.configure(yscrollincrement=SCROLL_INCREMENT_PIXELS)
        rows_host.bind("<MouseWheel>", lambda event: self._handleMouseWheel(rows_host, event))
        canvas.bind("<MouseWheel>", lambda event: self._handleMouseWheel(rows_host, event))
        rows_host.bind("<Button-4>", lambda event: self._handleMouseWheel(rows_host, event))
        rows_host.bind("<Button-5>", lambda event: self._handleMouseWheel(rows_host, event))
        canvas.bind("<Button-4>", lambda event: self._handleMouseWheel(rows_host, event))
        canvas.bind("<Button-5>", lambda event: self._handleMouseWheel(rows_host, event))

    def _bindRowInteractivity(self, row, row_key: int) -> None:
        def apply_color(color: str) -> None:
            row.configure(fg_color=color)

        def handle_enter(_event) -> None:
            is_selected = self._selectedItemKey == row_key
            apply_color(self._rowHoverColor(is_selected, getattr(row, "_comparison_status", None)))

        def handle_leave(_event) -> None:
            is_selected = self._selectedItemKey == row_key
            apply_color(self._rowColor(is_selected, getattr(row, "_comparison_status", None)))

        def handle_select(_event) -> None:
            self._selectedItemKey = row_key
            self._syncSelectionStyles()
            self._refreshDetailFromSelection(self._pagination.currentItems())

        bindRecursive(row, "<Enter>", handle_enter)
        bindRecursive(row, "<Leave>", handle_leave)
        bindRecursive(row, "<Button-1>", handle_select)
        bindRecursive(row, "<Double-Button-1>", lambda _event: self._openResultDetailByKey(row_key))
        bindRecursive(
            row,
            "<MouseWheel>",
            lambda event: self._handleMouseWheel(self._rowsHost, event),
        )
        bindRecursive(
            row,
            "<Button-4>",
            lambda event: self._handleMouseWheel(self._rowsHost, event),
        )
        bindRecursive(
            row,
            "<Button-5>",
            lambda event: self._handleMouseWheel(self._rowsHost, event),
        )

    def _handleMouseWheel(self, rows_host: ctk.CTkScrollableFrame, event) -> str:
        canvas = getattr(rows_host, "_parent_canvas", None)
        if canvas is None:
            return "break"

        if getattr(event, "num", None) == 4:
            canvas.yview_scroll(-FAST_MOUSE_WHEEL_UNITS, "units")
            return "break"
        if getattr(event, "num", None) == 5:
            canvas.yview_scroll(FAST_MOUSE_WHEEL_UNITS, "units")
            return "break"

        delta = getattr(event, "delta", 0)
        if delta == 0:
            return "break"
        direction = -1 if delta > 0 else 1
        canvas.yview_scroll(direction * FAST_MOUSE_WHEEL_UNITS, "units")
        return "break"

    def _scrollRowsToTop(self) -> None:
        canvas = getattr(self._rowsHost, "_parent_canvas", None)
        if canvas is None:
            return
        canvas.yview_moveto(0)

    def _showEmptyState(self) -> None:
        card = createFrame(
            self._rowsHost,
            theme=self._theme,
            fg_color="transparent",
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        createLabel(
            card,
            "Todavia no hay resultados de comparacion",
            theme=self._theme,
            font=("Segoe UI", 14, "bold"),
            wraplength=720,
        ).pack(anchor="w", padx=10, pady=(10, 4))
        local_song_hint = ""
        if self._allLocalSongs:
            local_song_hint = (
                f" La biblioteca activa ya tiene {len(self._allLocalSongs)} canciones cargadas,"
                " pero aun no se ha calculado la comparacion."
            )
        createLabel(
            card,
            (
                "Activa una playlist de YouTube y una biblioteca local para comparar,"
                ' o pulsa "Refrescar" para recalcular la tabla.'
                f"{local_song_hint}"
            ),
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=720,
        ).pack(anchor="w", padx=10, pady=(0, 10))
        card.pack(fill="x")

    def _buildRowSeparator(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=self._theme["border"],
            corner_radius=0,
            height=1,
            border_width=0,
        )

    def _rowColor(
        self,
        is_selected: bool,
        comparison_status: ComparisonStatus | None = None,
    ) -> str:
        if is_selected:
            return self._theme["accent_soft"]
        if comparison_status is ComparisonStatus.MISSING:
            return "#2B1D1D" if not is_selected else self._theme["accent_soft"]
        if comparison_status is ComparisonStatus.POSSIBLE_MATCH:
            return "#1F2836" if not is_selected else self._theme["accent_soft"]
        return "transparent"

    def _rowHoverColor(
        self,
        is_selected: bool,
        comparison_status: ComparisonStatus | None = None,
    ) -> str:
        if is_selected:
            return self._theme["accent_soft"]
        if comparison_status is ComparisonStatus.MISSING:
            return "#382323"
        if comparison_status is ComparisonStatus.POSSIBLE_MATCH:
            return "#273347"
        return self._theme["hover"]

    def _rowBorderWidth(self, comparison_status: ComparisonStatus | None) -> int:
        if comparison_status in (
            ComparisonStatus.MISSING,
            ComparisonStatus.POSSIBLE_MATCH,
        ):
            return 1
        return 0

    def _rowBorderColor(self, comparison_status: ComparisonStatus | None) -> str:
        if comparison_status is ComparisonStatus.MISSING:
            return self._theme["danger"]
        if comparison_status is ComparisonStatus.POSSIBLE_MATCH:
            return self._theme["accent"]
        return self._theme["border"]

    def _syncSelectionStyles(self) -> None:
        for child in self._rowsHost.winfo_children():
            row_key = getattr(child, "_comparison_row_key", None)
            is_selected = row_key == self._selectedItemKey
            child.configure(
                fg_color=self._rowColor(
                    is_selected,
                    getattr(child, "_comparison_status", None),
                )
            )

    def _refreshDetailFromSelection(
        self,
        page_items: list[PlaylistComparisonItemResultDto],
    ) -> None:
        selected_item = next(
            (
                item
                for item in page_items
                if item.youtube_playlist_item_id == self._selectedItemKey
            ),
            None,
        )
        if selected_item is None:
            self._showEmptyDetail()
            return

        row_data = buildComparisonTableRowViewData(selected_item)
        linked_local_song = self._resolveLinkedLocalSong(selected_item)
        linked_local_song_summary = buildComparisonLinkedLocalSongSummary(
            selected_item,
            linked_local_song,
        )
        self._detailSummaryLabel.configure(
            text=(
                f"Playlist: {row_data.playlist_title} · {row_data.playlist_artist}\n"
                f"Local: {row_data.local_match}\n"
                f"Disponibilidad: {row_data.availability_summary}\n"
                f"Revision: {row_data.review_note} | Score: {row_data.score_label}"
            ),
            text_color=self._theme["text_secondary"],
        )
        self._detailLinkedSongLabel.configure(
            text=(
                f"{linked_local_song_summary.title}\n"
                f"{linked_local_song_summary.detail}"
            ),
            text_color=self._theme["text_secondary"],
        )
        self._detailReasonLabel.configure(
            text=f"Motivo detectado: {row_data.reason_summary}",
            text_color=self._theme["text_muted"],
        )
        self._openDetailButton.configure(state="normal")

    def _showEmptyDetail(self) -> None:
        self._detailSummaryLabel.configure(
            text="Selecciona una fila para revisar la coincidencia local y el motivo detectado.",
            text_color=self._theme["text_secondary"],
        )
        self._detailLinkedSongLabel.configure(
            text="",
            text_color=self._theme["text_secondary"],
        )
        self._detailReasonLabel.configure(text="", text_color=self._theme["text_muted"])
        self._openDetailButton.configure(state="disabled")

    def _configureTableColumns(self, widget) -> None:
        for column_index, (_title, weight, _anchor) in enumerate(TABLE_COLUMNS):
            widget.grid_columnconfigure(column_index, weight=weight)

    def _resolveLinkedLocalSong(
        self,
        comparison_item: PlaylistComparisonItemResultDto,
    ) -> LocalSongDto | None:
        if comparison_item.local_song_id is None:
            return None
        return self._localSongsById.get(comparison_item.local_song_id)

    def _openSelectedResultDetail(self) -> None:
        if self._selectedItemKey is None:
            return
        self._openResultDetailByKey(self._selectedItemKey)

    def _openResultDetailByKey(self, row_key: int) -> None:
        comparison_item = self._findComparisonItemByKey(row_key)
        if comparison_item is None:
            return
        self._selectedItemKey = row_key
        self._syncSelectionStyles()
        self._refreshDetailFromSelection(self._pagination.currentItems())
        linked_local_song = self._resolveLinkedLocalSong(comparison_item)
        detail_view_data = buildComparisonResultDetailViewData(
            comparison_item,
            linked_local_song,
        )
        if self._detailDialog is not None and self._detailDialog.winfo_exists():
            self._detailDialog.destroy()
        self._detailDialog = ComparisonResultDetailDialog(
            self,
            self._theme,
            detail_view_data,
        )
        self._detailDialog.focus()

    def _findComparisonItemByKey(self, row_key: int) -> PlaylistComparisonItemResultDto | None:
        for comparison_item in self._allComparisonItems:
            if comparison_item.youtube_playlist_item_id == row_key:
                return comparison_item
        return None
