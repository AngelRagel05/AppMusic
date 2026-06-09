from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonResultDetailViewData import (
    buildComparisonResultDetailViewData,
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
from app.presentation.features.comparison.comparisonTableRowViewData import (
    buildComparisonTableRowViewData,
)
from app.presentation.features.comparison.ui.comparisonPage.comparisonResultDetailDialog.comparisonResultDetailDialog import (
    ComparisonResultDetailDialog,
)
from app.presentation.styles import createFrame, createLabel, createOptionMenu
from app.shared.constants.comparison import ComparisonStatus


PAGE_SIZE_VALUES = ("25", "50", "75", "100")
DEFAULT_PAGE_SIZE = 25
ROW_HEIGHT = 30
STATUS_TEXT_MAX_LENGTH = 8
TITLE_TEXT_MAX_LENGTH = 42
ARTIST_TEXT_MAX_LENGTH = 24
LOCAL_MATCH_TEXT_MAX_LENGTH = 34
REVIEW_TEXT_MAX_LENGTH = 22
TABLE_COLUMNS: tuple[tuple[str, str, int, bool], ...] = (
    ("status", "Estado", 80, False),
    ("playlist_title", "Titulo playlist", 360, True),
    ("playlist_artist", "Artista", 210, True),
    ("local_match", "Coincidencia local", 260, True),
    ("score", "Score", 70, False),
    ("review_note", "Revision", 220, True),
)


class ComparisonSplitSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        self._allLocalSongs: list[LocalSongDto] = []
        self._localSongsById: dict[int, LocalSongDto] = {}
        self._allComparisonItems: list[PlaylistComparisonItemResultDto] = []
        self._filteredComparisonItems: list[PlaylistComparisonItemResultDto] = []
        self._selectedComparisonFilter = ALL_COMPARISON_FILTER
        self._searchQuery = ""
        self._selectedItemKey: int | None = None
        self._detailDialog: ComparisonResultDetailDialog | None = None
        self._suspendNextSelectionOpen = False
        self._pagination = ComparisonPaginationState(DEFAULT_PAGE_SIZE)
        self._treeStyleName = f"comparisonResults{hex(id(self))}.Treeview"
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
        card.grid_columnconfigure(0, weight=1)
        card.grid(row=0, column=0, sticky="nsew")

        header = createFrame(card, theme=self._theme, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
        header.grid_columnconfigure(0, weight=1)
        createLabel(
            header,
            "Tabla de resultados de comparacion",
            theme=self._theme,
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self._countLabel = createLabel(
            header,
            "0 resultados",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 10),
        )
        self._countLabel.grid(row=0, column=1, sticky="e")

        controls = createFrame(card, theme=self._theme, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 2))
        controls.grid_columnconfigure(0, weight=1)
        self._pageLabel = createLabel(
            controls,
            "Sin resultados",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        self._pageLabel.grid(row=0, column=0, sticky="w")

        controls_right = createFrame(controls, theme=self._theme, fg_color="transparent")
        controls_right.grid(row=0, column=1, sticky="e")
        createLabel(
            controls_right,
            "Por pag.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(0, 8))
        self._pageSizeVariable = ctk.StringVar(value=str(DEFAULT_PAGE_SIZE))
        page_size_menu = createOptionMenu(
            controls_right,
            self._pageSizeVariable,
            values=PAGE_SIZE_VALUES,
            theme=self._theme,
            width=70,
        )
        page_size_menu.configure(font=("Segoe UI", 10), height=28)
        page_size_menu.configure(command=self._handlePageSizeChanged)
        page_size_menu.pack(side="left", padx=(0, 8))

        self._previousButton = ctk.CTkButton(
            controls_right,
            text="< Anterior",
            height=28,
            width=84,
            corner_radius=int(self._theme["radius_sm"]),
            fg_color=self._theme["surface"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            border_width=0,
            font=("Segoe UI", 10),
            command=self._handlePreviousPageRequested,
        )
        self._previousButton.pack(side="left", padx=(0, 6))
        self._nextButton = ctk.CTkButton(
            controls_right,
            text="Siguiente >",
            height=28,
            width=84,
            corner_radius=int(self._theme["radius_sm"]),
            fg_color=self._theme["surface"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            border_width=0,
            font=("Segoe UI", 10),
            command=self._handleNextPageRequested,
        )
        self._nextButton.pack(side="left")

        table = createFrame(
            card,
            theme=self._theme,
            fg_color=self._theme["surface"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        table.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)

        self._emptyState = createFrame(table, theme=self._theme, fg_color="transparent")
        self._emptyState.grid(row=0, column=0, sticky="nsew")
        self._emptyState.grid_columnconfigure(0, weight=1)

        self._treeContainer = createFrame(table, theme=self._theme, fg_color="transparent")
        self._treeContainer.grid(row=0, column=0, sticky="nsew")
        self._treeContainer.grid_rowconfigure(0, weight=1)
        self._treeContainer.grid_columnconfigure(0, weight=1)

        self._configureTreeStyle()
        self._buildTree()
        self._refreshResultsTable()

    def _configureTreeStyle(self) -> None:
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            self._treeStyleName,
            background=self._theme["surface"],
            fieldbackground=self._theme["surface"],
            foreground=self._theme["text"],
            borderwidth=0,
            relief="flat",
            rowheight=ROW_HEIGHT,
            font=("Segoe UI", 10),
        )
        style.configure(
            f"{self._treeStyleName}.Heading",
            background=self._theme["panel"],
            foreground=self._theme["text_muted"],
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=(6, 6),
        )
        style.map(
            self._treeStyleName,
            background=[("selected", self._theme["accent_soft"])],
            foreground=[("selected", self._theme["text"])],
        )
        style.map(
            f"{self._treeStyleName}.Heading",
            background=[("active", self._theme["panel"])],
            foreground=[("active", self._theme["text_muted"])],
        )

    def _buildTree(self) -> None:
        columns = [column_key for column_key, _title, _width, _stretch in TABLE_COLUMNS]
        self._tree = ttk.Treeview(
            self._treeContainer,
            columns=columns,
            show="headings",
            style=self._treeStyleName,
            selectmode="browse",
        )
        self._tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            self._treeContainer,
            orient="vertical",
            command=self._tree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=scrollbar.set)

        for column_key, title, width, stretch in TABLE_COLUMNS:
            anchor = tk.E if column_key == "score" else tk.W
            self._tree.heading(column_key, text=title, anchor=anchor)
            self._tree.column(
                column_key,
                anchor=anchor,
                width=width,
                minwidth=width,
                stretch=stretch,
            )

        self._tree.tag_configure(
            "missing",
            background="#1D1919",
            foreground=self._theme["text"],
        )
        self._tree.tag_configure(
            "possible_match",
            background="#1B212B",
            foreground=self._theme["text"],
        )
        self._tree.tag_configure(
            "found",
            background=self._theme["surface"],
            foreground=self._theme["text"],
        )
        self._tree.bind("<<TreeviewSelect>>", self._handleTreeSelectionChanged)
        self._tree.bind("<ButtonRelease-1>", self._handleTreeRowClicked)
        self._tree.bind("<Double-1>", self._handleTreeRowDoubleClicked)
        self._tree.bind("<Escape>", lambda _event: self._closeDetailDialog())

    def _refreshResultsTable(self) -> None:
        filtered_comparison_items = filterComparisonItemsByStatus(
            self._allComparisonItems,
            self._selectedComparisonFilter,
        )
        filtered_comparison_items = filterComparisonItemsByQuery(
            filtered_comparison_items,
            self._searchQuery,
        )
        self._filteredComparisonItems = list(filtered_comparison_items)
        self._pagination.setItems(filtered_comparison_items)

        visible_ids = {item.youtube_playlist_item_id for item in filtered_comparison_items}
        if self._selectedItemKey not in visible_ids:
            self._selectedItemKey = None

        self._refreshTableLabels()
        self._clearTreeRows()
        page_items = self._pagination.currentItems()
        if not page_items:
            self._showEmptyState()
            return

        self._treeContainer.tkraise()
        if self._selectedItemKey is None:
            self._selectedItemKey = page_items[0].youtube_playlist_item_id

        for comparison_item in page_items:
            self._insertTreeRow(comparison_item)

        selected_item_id = str(self._selectedItemKey)
        if self._tree.exists(selected_item_id):
            self._suspendNextSelectionOpen = True
            self._tree.selection_set(selected_item_id)
            self._tree.focus(selected_item_id)
            self._tree.see(selected_item_id)

    def _insertTreeRow(self, comparison_item: PlaylistComparisonItemResultDto) -> None:
        row_data = buildComparisonTableRowViewData(comparison_item)
        self._tree.insert(
            "",
            "end",
            iid=str(comparison_item.youtube_playlist_item_id),
            values=(
                self._statusChipLabel(comparison_item.comparison_status),
                self._truncateText(row_data.playlist_title, TITLE_TEXT_MAX_LENGTH),
                self._truncateText(row_data.playlist_artist, ARTIST_TEXT_MAX_LENGTH),
                self._truncateText(row_data.local_match, LOCAL_MATCH_TEXT_MAX_LENGTH),
                row_data.score_label,
                self._truncateText(row_data.review_note, REVIEW_TEXT_MAX_LENGTH),
            ),
            tags=(comparison_item.comparison_status.value,),
        )

    def _handlePageSizeChanged(self, selected_value: str) -> None:
        self._pagination.setPageSize(int(selected_value))
        self._refreshResultsTable()

    def _handlePreviousPageRequested(self) -> None:
        self._pagination.previousPage()
        self._refreshResultsTable()

    def _handleNextPageRequested(self) -> None:
        self._pagination.nextPage()
        self._refreshResultsTable()

    def _handleTreeSelectionChanged(self, _event) -> None:
        if self._suspendNextSelectionOpen:
            self._suspendNextSelectionOpen = False
        focused_item_id = self._tree.focus()
        if not focused_item_id:
            return
        self._selectedItemKey = int(focused_item_id)

    def _handleTreeRowClicked(self, event) -> None:
        row_id = self._tree.identify_row(event.y)
        if not row_id:
            return
        self._tree.focus(row_id)
        self._tree.selection_set(row_id)
        self._selectedItemKey = int(row_id)
        self._openResultDetailByKey(self._selectedItemKey)

    def _handleTreeRowDoubleClicked(self, event) -> None:
        row_id = self._tree.identify_row(event.y)
        if not row_id:
            return
        self._tree.focus(row_id)
        self._tree.selection_set(row_id)
        self._selectedItemKey = int(row_id)
        self._openResultDetailByKey(self._selectedItemKey)

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

    def _showEmptyState(self) -> None:
        self._emptyState.tkraise()
        for child in self._emptyState.winfo_children():
            child.destroy()

        card = createFrame(
            self._emptyState,
            theme=self._theme,
            fg_color="transparent",
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        card.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        createLabel(
            card,
            "Todavia no hay resultados de comparacion",
            theme=self._theme,
            font=("Segoe UI", 12, "bold"),
            wraplength=720,
        ).pack(anchor="w", padx=8, pady=(8, 2))
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
            font=("Segoe UI", 10),
            wraplength=720,
        ).pack(anchor="w", padx=8, pady=(0, 8))

    def _clearTreeRows(self) -> None:
        for item_id in self._tree.get_children():
            self._tree.delete(item_id)

    def _resolveLinkedLocalSong(
        self,
        comparison_item: PlaylistComparisonItemResultDto,
    ) -> LocalSongDto | None:
        if comparison_item.local_song_id is None:
            return None
        return self._localSongsById.get(comparison_item.local_song_id)

    def _truncateText(self, value: str, max_length: int) -> str:
        compact_value = " ".join(str(value).split())
        if len(compact_value) <= max_length:
            return compact_value
        if max_length <= 3:
            return compact_value[:max_length]
        return f"{compact_value[: max_length - 3]}..."

    def _statusChipLabel(self, status: ComparisonStatus) -> str:
        return {
            ComparisonStatus.FOUND: "OK",
            ComparisonStatus.MISSING: "FALTA",
            ComparisonStatus.POSSIBLE_MATCH: "POSIBLE",
        }[status]

    def _openResultDetailByKey(self, row_key: int) -> None:
        comparison_item = self._findComparisonItemByKey(row_key)
        if comparison_item is None:
            return

        linked_local_song = self._resolveLinkedLocalSong(comparison_item)
        detail_view_data = buildComparisonResultDetailViewData(
            comparison_item,
            linked_local_song,
        )
        self._closeDetailDialog()
        self._detailDialog = ComparisonResultDetailDialog(
            self,
            self._theme,
            detail_view_data,
        )
        self._detailDialog.focus()

    def _closeDetailDialog(self) -> None:
        if self._detailDialog is None:
            return
        if self._detailDialog.winfo_exists():
            self._suspendNextSelectionOpen = True
            self._detailDialog.destroy()
        self._detailDialog = None

    def _findComparisonItemByKey(self, row_key: int) -> PlaylistComparisonItemResultDto | None:
        for comparison_item in self._filteredComparisonItems:
            if comparison_item.youtube_playlist_item_id == row_key:
                return comparison_item
        return None
