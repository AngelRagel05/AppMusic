from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonSearch import (
    filterComparisonItemsByQuery,
    filterLocalSongsByQuery,
)
from app.presentation.features.comparison.comparisonAvailabilitySummary import (
    buildComparisonAvailabilitySummary,
)
from app.presentation.features.comparison.comparisonPaginationState import (
    ComparisonPaginationState,
)
from app.presentation.features.comparison.comparisonReasonSummary import (
    buildComparisonReasonSummary,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    ALL_COMPARISON_FILTER,
    filterComparisonItemsByStatus,
)
from app.presentation.styles import (
    ActionButton,
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
ROW_HEIGHT = 32


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
    rowKeyAccessor: Callable
    pagination: ComparisonPaginationState
    renderToken: int = 0
    selectedItemKey: object | None = None


class ComparisonSplitSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        self._allLocalSongs: list[LocalSongDto] = []
        self._allComparisonItems: list[PlaylistComparisonItemResultDto] = []
        self._selectedComparisonFilter = ALL_COMPARISON_FILTER
        self._searchQuery = ""
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._localSongsColumn = self._buildColumnCard(
            title="Canciones de biblioteca local",
            empty_title="Todavía no hay canciones locales visibles",
            empty_message="Activa una biblioteca local y sincronizala para ver aqui su detalle.",
            singular_label="canción local",
            plural_label="canciones locales",
            build_row=self._buildLocalSongRow,
            row_key_accessor=lambda local_song: local_song.id or local_song.file_path,
        )
        self._localSongsColumn.card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._comparisonResultsColumn = self._buildColumnCard(
            title="Resultados de comparación",
            empty_title="Todavía no hay resultados de comparación",
            empty_message="Activa una playlist de YouTube y una biblioteca local para comparar.",
            singular_label="resultado",
            plural_label="resultados",
            build_row=self._buildComparisonResultRow,
            row_key_accessor=lambda comparison_item: comparison_item.youtube_playlist_item_id,
        )
        self._comparisonResultsColumn.card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0),
        )

    def showLocalSongs(self, local_songs: list[LocalSongDto]) -> None:
        self._allLocalSongs = list(local_songs)
        self._refreshLocalSongsColumn()

    def showComparisonData(
        self,
        local_songs: list[LocalSongDto],
        comparison_items: list[PlaylistComparisonItemResultDto],
    ) -> None:
        self._allLocalSongs = list(local_songs)
        self._allComparisonItems = list(comparison_items)
        self._refreshLocalSongsColumn()
        self._refreshComparisonResultsColumn()

    def showComparisonResults(
        self,
        comparison_items: list[PlaylistComparisonItemResultDto],
    ) -> None:
        self._allComparisonItems = list(comparison_items)
        self._refreshComparisonResultsColumn()

    def setComparisonFilter(self, selected_filter: str) -> None:
        self._selectedComparisonFilter = selected_filter
        self._refreshComparisonResultsColumn()

    def setSearchQuery(self, query: str) -> None:
        self._searchQuery = query
        self._refreshLocalSongsColumn()
        self._refreshComparisonResultsColumn()

    def _buildColumnCard(
        self,
        *,
        title: str,
        empty_title: str,
        empty_message: str,
        singular_label: str,
        plural_label: str,
        build_row: Callable,
        row_key_accessor: Callable,
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
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
        header.grid_columnconfigure(0, weight=1)
        createLabel(
            header,
            title,
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")
        count_label = createLabel(
            header,
            "0",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12),
        )
        count_label.grid(row=0, column=1, sticky="e")

        controls = createFrame(card, theme=self._theme, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
        controls.grid_columnconfigure(0, weight=1)
        page_label = createLabel(
            controls,
            "Sin resultados",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
        )
        page_label.grid(row=0, column=0, sticky="w")

        controls_right = createFrame(controls, theme=self._theme, fg_color="transparent")
        controls_right.grid(row=0, column=1, sticky="e")
        createLabel(
            controls_right,
            "Por pag.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(0, 8))
        page_size_variable = ctk.StringVar(value=str(DEFAULT_PAGE_SIZE))
        page_size_menu = createOptionMenu(
            controls_right,
            page_size_variable,
            values=PAGE_SIZE_VALUES,
            theme=self._theme,
            width=70,
        )
        page_size_menu.configure(font=("Segoe UI", 11))
        page_size_menu.pack(side="left", padx=(0, 8))
        previous_button = ActionButton(
            controls_right,
            text="< Anterior",
            variant="secondary",
            theme=self._theme,
            height=28,
        )
        previous_button.widget.configure(width=84, font=("Segoe UI", 11))
        previous_button.widget.pack(side="left", padx=(0, 6))
        next_button = ActionButton(
            controls_right,
            text="Siguiente >",
            variant="secondary",
            theme=self._theme,
            height=28,
        )
        next_button.widget.configure(width=84, font=("Segoe UI", 11))
        next_button.widget.pack(side="left")

        rows_host = createScrollableFrame(card, theme=self._theme, fg_color="transparent")
        rows_host.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

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
            rowKeyAccessor=row_key_accessor,
            pagination=ComparisonPaginationState(DEFAULT_PAGE_SIZE),
        )
        previous_button.clicked.connect(lambda: self._handlePreviousPageRequested(column_state))
        next_button.clicked.connect(lambda: self._handleNextPageRequested(column_state))
        page_size_menu.configure(
            command=lambda selected_value: self._handlePageSizeChanged(column_state, selected_value)
        )
        self._configureFastScroll(column_state.rowsHost)
        self._refreshColumn(column_state)
        return column_state

    def _setItems(self, column_state: ComparisonColumnState, items) -> None:
        column_state.pagination.setItems(items)
        self._refreshColumn(column_state)

    def _refreshLocalSongsColumn(self) -> None:
        filtered_local_songs = filterLocalSongsByQuery(
            self._allLocalSongs,
            self._searchQuery,
        )
        self._setItems(self._localSongsColumn, filtered_local_songs)

    def _refreshComparisonResultsColumn(self) -> None:
        filtered_comparison_items = filterComparisonItemsByStatus(
            self._allComparisonItems,
            self._selectedComparisonFilter,
        )
        filtered_comparison_items = filterComparisonItemsByQuery(
            filtered_comparison_items,
            self._searchQuery,
        )
        self._setItems(self._comparisonResultsColumn, filtered_comparison_items)

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
        self._scrollColumnToTop(column_state.rowsHost)
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
                    f"Pág. {column_state.pagination.currentPage}/{column_state.pagination.totalPages}"
                    f"  {range_start}-{range_end}"
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
            row_key = column_state.rowKeyAccessor(item)
            row = column_state.buildRow(
                column_state.rowsHost,
                item,
                column_state.selectedItemKey == row_key,
            )
            row._comparison_row_key = row_key
            row._comparison_status = getattr(item, "comparison_status", None)
            self._bindRowInteractivity(column_state, row, row_key)
            row.pack(fill="x")

        if end_index < len(items):
            column_state.rowsHost.after(
                0,
                lambda: self._appendRowsChunk(column_state, items, end_index, render_token),
            )

    def _buildLocalSongRow(self, parent, local_song: LocalSongDto, is_selected: bool):
        row = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._rowColor(is_selected),
            corner_radius=int(self._theme["radius_sm"]),
        )
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        row.grid_propagate(False)
        row.configure(height=ROW_HEIGHT)

        title = local_song.title or local_song.file_name
        artist = local_song.artist or "Artista desconocido"
        createLabel(
            row,
            title,
            theme=self._theme,
            font=("Segoe UI", 12),
            text_color=self._theme["text"],
            wraplength=0,
        ).grid(row=0, column=0, sticky="ew", padx=(6, 8), pady=(4, 3))
        createLabel(
            row,
            artist,
            theme=self._theme,
            font=("Segoe UI", 12),
            text_color=self._theme["text_secondary"],
            anchor="e",
            justify="right",
            wraplength=0,
        ).grid(row=0, column=1, sticky="e", padx=(8, 6), pady=(4, 3))
        self._buildRowSeparator(row).grid(row=1, column=0, sticky="ew")
        self._buildRowSeparator(row).grid(row=1, column=1, sticky="ew")
        return row

    def _buildComparisonResultRow(
        self,
        parent,
        comparison_item: PlaylistComparisonItemResultDto,
        is_selected: bool,
    ):
        row = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._rowColor(is_selected, comparison_item.comparison_status),
            corner_radius=int(self._theme["radius_sm"]),
            border_width=self._rowBorderWidth(comparison_item.comparison_status),
            border_color=self._rowBorderColor(comparison_item.comparison_status),
        )
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        row.grid_rowconfigure(0, weight=1)
        row.grid_rowconfigure(1, weight=1)
        title_row = createFrame(row, theme=self._theme, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew", padx=6, pady=(2, 0))
        title_row.grid_columnconfigure(0, weight=1)
        createLabel(
            title_row,
            f"{comparison_item.youtube_title} - {comparison_item.youtube_artist}",
            theme=self._theme,
            font=("Segoe UI", 11),
            wraplength=0,
        ).grid(row=0, column=0, sticky="w")
        createLabel(
            row,
            self._buildAvailabilityMessage(comparison_item),
            theme=self._theme,
            text_color=self._availabilityColor(comparison_item.comparison_status),
            font=("Segoe UI", 11, "bold"),
            wraplength=0,
        ).grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 0))
        self._buildStatusBadge(row, comparison_item.comparison_status).grid(
            row=0,
            column=1,
            rowspan=3,
            padx=(6, 6),
        )
        createLabel(
            row,
            self._buildCandidateMessage(comparison_item),
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=0,
        ).grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 3))
        self._buildRowSeparator(row).grid(row=3, column=0, columnspan=2, sticky="ew")
        return row

    def _buildStatusBadge(self, parent, status: ComparisonStatus):
        status_text = {
            ComparisonStatus.FOUND: "Encontrada",
            ComparisonStatus.MISSING: "Falta",
            ComparisonStatus.POSSIBLE_MATCH: "Posible coincidencia",
        }[status]
        status_color = {
            ComparisonStatus.FOUND: self._theme["success"],
            ComparisonStatus.MISSING: self._theme["danger"],
            ComparisonStatus.POSSIBLE_MATCH: self._theme["accent"],
        }[status]
        badge = createFrame(
            parent,
            theme=self._theme,
            fg_color="transparent",
            corner_radius=int(self._theme["radius_sm"]),
            border_width=0,
        )
        createLabel(
            badge,
            status_text,
            theme=self._theme,
            text_color=status_color,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="center", padx=0, pady=0)
        return badge

    def _buildCandidateMessage(self, comparison_item: PlaylistComparisonItemResultDto) -> str:
        reason_summary = buildComparisonReasonSummary(comparison_item)
        if comparison_item.local_title and comparison_item.local_artist:
            return (
                f"Local: {comparison_item.local_title} · {comparison_item.local_artist}"
                f" | {reason_summary}"
            )
        if comparison_item.local_title:
            return f"Local: {comparison_item.local_title} | {reason_summary}"
        if comparison_item.comparison_status is ComparisonStatus.MISSING:
            return f"Local: sin coincidencia encontrada | {reason_summary}"
        return f"Local: candidata sin metadata completa | {reason_summary}"

    def _buildAvailabilityMessage(
        self,
        comparison_item: PlaylistComparisonItemResultDto,
    ) -> str:
        return buildComparisonAvailabilitySummary(comparison_item)

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

    def _bindRowInteractivity(
        self,
        column_state: ComparisonColumnState,
        row,
        row_key: object,
    ) -> None:
        rows_host = column_state.rowsHost
        def apply_color(color: str) -> None:
            row.configure(fg_color=color)

        def handle_enter(_event) -> None:
            is_selected = column_state.selectedItemKey == row_key
            apply_color(self._rowHoverColor(is_selected, getattr(row, "_comparison_status", None)))

        def handle_leave(_event) -> None:
            is_selected = column_state.selectedItemKey == row_key
            apply_color(self._rowColor(is_selected, getattr(row, "_comparison_status", None)))

        def handle_select(_event) -> None:
            column_state.selectedItemKey = row_key
            self._syncSelectionStyles(column_state)

        bindRecursive(row, "<Enter>", handle_enter)
        bindRecursive(row, "<Leave>", handle_leave)
        bindRecursive(row, "<Button-1>", handle_select)
        bindRecursive(
            row,
            "<MouseWheel>",
            lambda event: self._handleMouseWheel(rows_host, event),
        )
        bindRecursive(
            row,
            "<Button-4>",
            lambda event: self._handleMouseWheel(rows_host, event),
        )
        bindRecursive(
            row,
            "<Button-5>",
            lambda event: self._handleMouseWheel(rows_host, event),
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

    def _scrollColumnToTop(self, rows_host: ctk.CTkScrollableFrame) -> None:
        canvas = getattr(rows_host, "_parent_canvas", None)
        if canvas is None:
            return
        canvas.yview_moveto(0)

    def _showEmptyState(self, parent, title: str, message: str) -> None:
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color="transparent",
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        createLabel(
            card,
            title,
            theme=self._theme,
            font=("Segoe UI", 14, "bold"),
            wraplength=320,
        ).pack(anchor="w", padx=10, pady=(10, 4))
        createLabel(
            card,
            message,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=320,
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
            return self._theme["surface"]
        if comparison_status is ComparisonStatus.POSSIBLE_MATCH:
            return self._theme["accent_soft"]
        return "transparent"

    def _rowHoverColor(
        self,
        is_selected: bool,
        comparison_status: ComparisonStatus | None = None,
    ) -> str:
        if is_selected:
            return self._theme["accent_soft"]
        if comparison_status is ComparisonStatus.MISSING:
            return self._theme["hover"]
        if comparison_status is ComparisonStatus.POSSIBLE_MATCH:
            return self._theme["hover"]
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

    def _syncSelectionStyles(self, column_state: ComparisonColumnState) -> None:
        for child in column_state.rowsHost.winfo_children():
            row_key = getattr(child, "_comparison_row_key", None)
            is_selected = row_key == column_state.selectedItemKey
            child.configure(
                fg_color=self._rowColor(
                    is_selected,
                    getattr(child, "_comparison_status", None),
                )
            )
