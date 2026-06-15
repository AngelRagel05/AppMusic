from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonLastRunSummary import (
    buildComparisonLastRunSummary,
    formatComparisonHistoryTimestamp,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    ALL_COMPARISON_FILTER,
    COMPARISON_FILTER_VALUES,
)
from app.presentation.features.comparison.ui.comparisonPage.comparisonSplitSection.comparisonSplitSection import (
    ComparisonSplitSection,
)
from app.presentation.styles import (
    applyButtonStyle,
    clearChildren,
    createEntry,
    createFrame,
    createLabel,
    createOptionMenu,
    getPageTheme,
)
from app.presentation.widgets.loadingOverlay import LoadingOverlay
from app.presentation.widgets.pageHeader.pageHeader import PageHeader


class ComparisonPage(ctk.CTkFrame):
    TOP_SECTION_RATIO = 0.17
    MINIMUM_TOP_SECTION_HEIGHT = 138
    DEFAULT_PRIMARY_ACTION_LABEL = "↻ Refrescar"
    RERUN_PRIMARY_ACTION_LABEL = "↻ Volver a comparar"
    HISTORY_COLUMNS: tuple[tuple[str, int | None, int, str, int], ...] = (
        ("Fecha", 132, 0, "w", 16),
        ("Biblioteca", None, 2, "w", 16),
        ("Playlist", None, 2, "w", 16),
        ("Encontradas", 86, 0, "e", 12),
        ("Posibles", 76, 0, "e", 10),
        ("Faltan", 68, 0, "e", 10),
    )

    def __init__(self, parent) -> None:
        self._theme = getPageTheme("comparison")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)
        self._defaultSubtitle = "Biblioteca local vs Playlist"
        self._is_built = False
        self._active_folder_name = "Sin biblioteca configurada"
        self._active_playlist_title = "Sin playlist configurada"
        self._pending_search_after_id: str | None = None
        self._search_variable: ctk.StringVar | None = None
        self._history_entries: list[PlaylistComparisonHistoryEntryDto] = []
        self._loadingOverlay = LoadingOverlay(self, self._theme)
        self._content: ctk.CTkFrame | None = None
        self._topSection: ctk.CTkFrame | None = None

    def activate(self) -> None:
        self._ensureBuilt()

    def showLocalSongs(self, local_songs: list[LocalSongDto]) -> None:
        self._ensureBuilt()
        self.section.showLocalSongs(local_songs)

    def onPrimaryActionRequested(self, callback: Callable[[], None]) -> None:
        self._ensureBuilt()
        self.header.primaryActionRequested.connect(callback)

    def onManualDecisionRequested(
        self,
        callback: Callable[[PlaylistComparisonItemResultDto, str, int | None], bool],
    ) -> None:
        self._ensureBuilt()
        self.section.setManualDecisionRequestedHandler(callback)

    def confirmManualComparisonStart(
        self,
        *,
        playlist_title: str,
        folder_name: str,
    ) -> bool:
        return messagebox.askokcancel(
            "Refrescar comparación",
            (
                "Esta accion volvera a calcular la comparacion entre:\n"
                f'• Playlist: "{playlist_title}"\n'
                f'• Biblioteca: "{folder_name}"\n\n'
                "Tambien actualizara el snapshot guardado en la base de datos.\n\n"
                "Puede tardar unos minutos dependiendo del tamaño de la biblioteca "
                "y la playlist.\n\n¿Quieres continuar ahora?"
            ),
            parent=self.winfo_toplevel(),
        )

    def showComparisonData(
        self,
        local_songs: list[LocalSongDto],
        comparison_result: PlaylistComparisonResultDto,
    ) -> None:
        self._ensureBuilt()
        self._foundCountValue.configure(text=str(comparison_result.summary.found_count))
        self._missingCountValue.configure(text=str(comparison_result.summary.missing_count))
        self._possibleMatchCountValue.configure(
            text=str(comparison_result.summary.possible_match_count)
        )
        self._updateLastComparisonLabel(comparison_result.last_compared_at)
        self.section.showComparisonData(local_songs, comparison_result.items)

    def showComparisonResults(
        self,
        comparison_result: PlaylistComparisonResultDto,
    ) -> None:
        self._ensureBuilt()
        self._foundCountValue.configure(text=str(comparison_result.summary.found_count))
        self._missingCountValue.configure(text=str(comparison_result.summary.missing_count))
        self._possibleMatchCountValue.configure(
            text=str(comparison_result.summary.possible_match_count)
        )
        self._updateLastComparisonLabel(comparison_result.last_compared_at)
        self.section.showComparisonResults(comparison_result.items)

    def showComparisonHistory(
        self,
        comparison_history: list[PlaylistComparisonHistoryEntryDto],
    ) -> None:
        self._history_entries = list(comparison_history)
        self._ensureBuilt()
        self._lastComparisonLabel.configure(
            text=buildComparisonLastRunSummary(self._history_entries)
        )
        self._renderHistoryEntries()

    def setActiveFolderName(self, name: str) -> None:
        self._active_folder_name = name
        if self._is_built:
            self.header.setActiveFolderName(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self._active_playlist_title = title
        if self._is_built:
            self.header.setActivePlaylistTitle(title)

    def showComparisonStatusMessage(self, message: str, tone: str = "info") -> None:
        self._ensureBuilt()
        tone_prefix = {
            "info": "Comparando",
            "success": "Resultado",
            "error": "Error",
        }.get(tone, "Comparación")
        self.header.setSubtitle(f"{tone_prefix}: {message}" if message else self._defaultSubtitle)

    def setPrimaryActionLabel(self, label: str) -> None:
        self._ensureBuilt()
        self.header.setActions(None, label)

    def showLoadingState(self, message: str) -> None:
        self._loadingOverlay.show(
            "Cargando comparación...",
            message,
        )

    def hideLoadingState(self) -> None:
        self._loadingOverlay.hide()

    def _ensureBuilt(self) -> None:
        if self._is_built:
            return

        content = createFrame(self, theme=self._theme, fg_color=self._theme["bg"])
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=0)
        content.grid_rowconfigure(1, weight=1)
        self._content = content

        top_section = createFrame(content, theme=self._theme, fg_color=self._theme["bg"])
        top_section.grid(row=0, column=0, sticky="nsew")
        top_section.grid_columnconfigure(0, weight=1)
        top_section.grid_propagate(False)
        self._topSection = top_section

        self.header = PageHeader(
            top_section,
            "Comparación",
            self._theme,
            subtitle=self._defaultSubtitle,
        )
        self.header.setContextVisible(False)
        self.header.setActions(None, self.DEFAULT_PRIMARY_ACTION_LABEL)
        applyButtonStyle(self.header.primaryButton.widget, "primary", self._theme)
        self.header.primaryButton.widget.configure(
            height=30,
            width=150,
            font=("Segoe UI", 11, "bold"),
        )
        self.section = ComparisonSplitSection(content, self._theme)
        self._summaryCards = self._buildSummaryCards(top_section)
        self._historyCard = self._buildHistoryCard(top_section)

        self.header.grid(row=0, column=0, sticky="ew")
        self._summaryCards.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self._historyCard.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self.section.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.header.setActiveFolderName(self._active_folder_name)
        self.header.setActivePlaylistTitle(self._active_playlist_title)
        self._renderHistoryEntries()
        content.bind("<Configure>", self._handleContentResize)
        self._is_built = True

    def _handleContentResize(self, event) -> None:
        if self._topSection is None:
            return

        target_height = max(
            self.MINIMUM_TOP_SECTION_HEIGHT,
            int(event.height * self.TOP_SECTION_RATIO),
        )
        self._topSection.configure(height=target_height)

    def _buildSummaryCards(self, parent):
        wrapper = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        wrapper.grid_columnconfigure(0, weight=0)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_columnconfigure(2, weight=0)

        summary_block = createFrame(wrapper, theme=self._theme, fg_color="transparent")
        summary_block.grid(row=0, column=0, sticky="w", padx=(8, 6), pady=6)
        self._foundCountValue = self._buildSummaryLine(
            summary_block,
            row=0,
            title="Encontradas",
            accent=self._theme["success"],
        )
        self._missingCountValue = self._buildSummaryLine(
            summary_block,
            row=0,
            column=2,
            title="Faltan",
            accent=self._theme["danger"],
        )
        self._possibleMatchCountValue = self._buildSummaryLine(
            summary_block,
            row=0,
            column=4,
            title="Coincidencias",
            accent=self._theme["accent"],
        )
        self._lastComparisonLabel = createLabel(
            summary_block,
            buildComparisonLastRunSummary(self._history_entries),
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        self._lastComparisonLabel.grid(
            row=1,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(6, 0),
        )

        search_block = createFrame(wrapper, theme=self._theme, fg_color="transparent")
        search_block.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(4, 8), pady=6)
        search_block.grid_columnconfigure(0, weight=1)
        search_variable = ctk.StringVar(value="")
        self._search_variable = search_variable
        search_entry = createEntry(
            search_block,
            theme=self._theme,
            width=420,
            placeholder_text="Buscar por titulo o artista...",
            textvariable=search_variable,
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        search_entry.configure(height=30, font=("Segoe UI", 11))
        search_variable.trace_add(
            "write",
            lambda *_args: self._scheduleSearchUpdate(),
        )

        filter_row = createFrame(search_block, theme=self._theme, fg_color="transparent")
        filter_row.grid(row=0, column=1, sticky="e")
        createLabel(
            filter_row,
            "Filtro:",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(0, 6))
        filter_variable = ctk.StringVar(value=ALL_COMPARISON_FILTER)
        filter_menu = createOptionMenu(
            filter_row,
            filter_variable,
            values=COMPARISON_FILTER_VALUES,
            theme=self._theme,
            width=126,
        )
        filter_menu.configure(font=("Segoe UI", 10), height=30)
        filter_menu.configure(command=self.section.setComparisonFilter)
        filter_menu.pack(side="left")
        return wrapper

    def _buildHistoryCard(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        card.grid_columnconfigure(0, weight=1)

        header = createFrame(card, theme=self._theme, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))
        header.grid_columnconfigure(0, weight=1)
        createLabel(
            header,
            "Historico reciente",
            theme=self._theme,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")
        createLabel(
            header,
            "Comparaciones guardadas disponibles del ambito activo",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        body = createFrame(card, theme=self._theme, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        body.grid_columnconfigure(0, weight=1)
        self._historyBody = body
        return card

    def _renderHistoryEntries(self) -> None:
        if not hasattr(self, "_historyBody"):
            return

        clearChildren(self._historyBody)
        if not self._history_entries:
            self._historyCard.grid()
            empty_row = createFrame(
                self._historyBody,
                theme=self._theme,
                fg_color=self._theme["surface"],
                corner_radius=int(self._theme["radius_sm"]),
            )
            empty_row.grid(row=0, column=0, sticky="ew")
            self._configureHistoryGridColumns(empty_row)
            empty_row.grid_propagate(False)
            empty_row.configure(height=38)
            createLabel(
                empty_row,
                "Sin comparaciones recientes",
                theme=self._theme,
                text_color=self._theme["text_secondary"],
                font=("Segoe UI", 10),
            ).grid(row=0, column=0, columnspan=len(self.HISTORY_COLUMNS), sticky="w", padx=8, pady=0)
            return
        self._historyCard.grid()
        header_row = createFrame(
            self._historyBody,
            theme=self._theme,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_sm"]),
        )
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        self._configureHistoryGridColumns(header_row)
        header_row.grid_propagate(False)
        header_row.configure(height=28)
        for column_index, (title, _minsize, _weight, anchor, _truncate) in enumerate(self.HISTORY_COLUMNS):
            createLabel(
                header_row,
                title,
                theme=self._theme,
                text_color=self._theme["text_muted"],
                font=("Segoe UI", 10, "bold"),
                anchor=anchor,
                justify="right" if anchor == "e" else "left",
            ).grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=(8 if column_index == 0 else 6, 8 if column_index == len(self.HISTORY_COLUMNS) - 1 else 6),
                pady=0,
            )

        for row_index, entry in enumerate(self._history_entries, start=1):
            row = createFrame(
                self._historyBody,
                theme=self._theme,
                fg_color=self._theme["surface"],
                corner_radius=int(self._theme["radius_sm"]),
            )
            row.grid(row=row_index, column=0, sticky="ew", pady=(0, 3))
            self._configureHistoryGridColumns(row)
            row.grid_propagate(False)
            row.configure(height=30)
            row_values = (
                self._formatHistoryTimestamp(entry.compared_at),
                self._active_folder_name,
                self._active_playlist_title,
                str(entry.found_count),
                str(entry.possible_match_count),
                str(entry.missing_count),
            )
            for column_index, value in enumerate(row_values):
                _title, _minsize, _weight, anchor, max_length = self.HISTORY_COLUMNS[column_index]
                createLabel(
                    row,
                    self._truncateText(value, max_length),
                    theme=self._theme,
                    text_color=self._theme["text_secondary"] if column_index < 3 else self._theme["text"],
                    font=("Segoe UI", 10),
                    anchor=anchor,
                    justify="right" if anchor == "e" else "left",
                    wraplength=0,
                ).grid(
                    row=0,
                    column=column_index,
                    sticky="ew",
                    padx=(8 if column_index == 0 else 6, 8 if column_index == len(self.HISTORY_COLUMNS) - 1 else 6),
                    pady=0,
                )

    def _scheduleSearchUpdate(self) -> None:
        if self._search_variable is None:
            return
        if self._pending_search_after_id is not None:
            self.after_cancel(self._pending_search_after_id)
        self._pending_search_after_id = self.after(500, self._applySearchQuery)

    def _applySearchQuery(self) -> None:
        self._pending_search_after_id = None
        if self._search_variable is None:
            return
        self.section.setSearchQuery(self._search_variable.get())

    def _buildSummaryLine(
        self,
        parent,
        *,
        row: int,
        title: str,
        accent: str,
        column: int = 0,
    ):
        value_label = createLabel(
            parent,
            "0",
            theme=self._theme,
            text_color=accent,
            font=("Segoe UI", int(self._theme["value_size"]), "bold"),
        )
        value_label.grid(row=row, column=column, sticky="w", pady=0)
        createLabel(
            parent,
            title,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 10),
        ).grid(row=row, column=column + 1, sticky="w", padx=(5, 12), pady=0)
        if column < 4:
            createLabel(
                parent,
                "|",
                theme=self._theme,
                text_color=self._theme["border"],
                font=("Segoe UI", 10),
            ).grid(row=row, column=column + 2, sticky="w", padx=(0, 10))
        return value_label

    def _buildHistoryEntryTitle(self, entry: PlaylistComparisonHistoryEntryDto) -> str:
        return f"Comparada el {self._formatHistoryTimestamp(entry.compared_at)}"

    def _formatHistoryTimestamp(self, value: datetime) -> str:
        return formatComparisonHistoryTimestamp(value)

    def _updateLastComparisonLabel(self, compared_at: datetime | None) -> None:
        if compared_at is None:
            return
        synthetic_history = [
            PlaylistComparisonHistoryEntryDto(
                comparison_id=0,
                compared_at=compared_at,
                found_count=0,
                missing_count=0,
                possible_match_count=0,
                total_compared=0,
            )
        ]
        self._lastComparisonLabel.configure(
            text=buildComparisonLastRunSummary(synthetic_history)
        )

    def _configureHistoryGridColumns(self, widget) -> None:
        for column_index, (_title, minsize, weight, _anchor, _truncate) in enumerate(self.HISTORY_COLUMNS):
            widget.grid_columnconfigure(
                column_index,
                minsize=minsize if minsize is not None else 0,
                weight=weight,
            )

    def _truncateText(self, value: str, max_length: int) -> str:
        compact_value = " ".join(str(value).split())
        if len(compact_value) <= max_length:
            return compact_value
        if max_length <= 3:
            return compact_value[:max_length]
        return f"{compact_value[: max_length - 3]}..."
