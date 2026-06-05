from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    ALL_COMPARISON_FILTER,
    COMPARISON_FILTER_VALUES,
)
from app.presentation.features.comparison.ui.comparisonPage.comparisonSplitSection.comparisonSplitSection import (
    ComparisonSplitSection,
)
from app.presentation.styles import (
    createEntry,
    createFrame,
    createLabel,
    createOptionMenu,
    getPageTheme,
)
from app.presentation.widgets.loadingOverlay import LoadingOverlay
from app.presentation.widgets.pageHeader.pageHeader import PageHeader


class ComparisonPage(ctk.CTkFrame):
    TOP_SECTION_RATIO = 0.25
    MINIMUM_TOP_SECTION_HEIGHT = 250

    def __init__(self, parent) -> None:
        self._theme = getPageTheme("overview")
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)
        self._defaultSubtitle = (
            "Consulta en paralelo las canciones de tu biblioteca activa y el estado de "
            "coincidencia de la playlist activa"
        )
        self._is_built = False
        self._active_folder_name = "Sin biblioteca configurada"
        self._active_playlist_title = "Sin playlist configurada"
        self._pending_search_after_id: str | None = None
        self._search_variable: ctk.StringVar | None = None
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

    def confirmManualComparisonStart(self) -> bool:
        return messagebox.askokcancel(
            "Refrescar comparación",
            (
                "Esta acción volverá a calcular la comparación y actualizará el "
                "snapshot guardado en la base de datos.\n\n"
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
        self.section.showComparisonResults(comparison_result.items)

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
        content.pack(fill="both", expand=True, padx=int(self._theme["page_padding"]), pady=36)
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
        self.header.setActions(None, "Refrescar comparación")
        self.section = ComparisonSplitSection(content, self._theme)
        self._summaryCards = self._buildSummaryCards(top_section)

        self.header.grid(row=0, column=0, sticky="ew")
        self._summaryCards.grid(row=1, column=0, sticky="ew", pady=(18, 0))
        self.section.grid(row=1, column=0, sticky="nsew", pady=(18, 0))
        self.header.setActiveFolderName(self._active_folder_name)
        self.header.setActivePlaylistTitle(self._active_playlist_title)
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
        wrapper = createFrame(parent, theme=self._theme, fg_color=self._theme["bg"])
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_columnconfigure(2, weight=1)
        wrapper.grid_columnconfigure(3, weight=1)

        self._foundCountValue = self._buildSummaryCard(
            wrapper,
            column=0,
            title="Encontradas",
            accent=self._theme["success"],
        )
        self._missingCountValue = self._buildSummaryCard(
            wrapper,
            column=1,
            title="Faltan",
            accent=self._theme["danger"],
        )
        self._possibleMatchCountValue = self._buildSummaryCard(
            wrapper,
            column=2,
            title="Posibles coincidencias",
            accent=self._theme["accent"],
        )

        search_card = createFrame(
            wrapper,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        search_card.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=(0, 9), pady=(14, 0))
        createLabel(
            search_card,
            "Buscador global",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=16, pady=(12, 6))
        search_variable = ctk.StringVar(value="")
        self._search_variable = search_variable
        search_entry = createEntry(
            search_card,
            theme=self._theme,
            width=520,
            placeholder_text="Busca por titulo, artista, album o texto relacionado...",
            textvariable=search_variable,
        )
        search_entry.pack(fill="x", padx=16, pady=(0, 12))
        search_variable.trace_add(
            "write",
            lambda *_args: self._scheduleSearchUpdate(),
        )

        filter_card = createFrame(
            wrapper,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        filter_card.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=(9, 0), pady=(0, 0))
        createLabel(
            filter_card,
            "Filtro de resultados",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=16, pady=(12, 6))
        filter_variable = ctk.StringVar(value=ALL_COMPARISON_FILTER)
        filter_menu = createOptionMenu(
            filter_card,
            filter_variable,
            values=COMPARISON_FILTER_VALUES,
            theme=self._theme,
            width=220,
        )
        filter_menu.configure(command=self.section.setComparisonFilter)
        filter_menu.pack(anchor="w", padx=16, pady=(0, 12))
        return wrapper

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

    def _buildSummaryCard(self, parent, *, column: int, title: str, accent: str):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        card.grid(row=0, column=column, sticky="nsew", padx=(0, 9))
        createLabel(
            card,
            title,
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=16, pady=(12, 6))
        value_label = createLabel(
            card,
            "0",
            theme=self._theme,
            text_color=accent,
            font=("Segoe UI", 24, "bold"),
        )
        value_label.pack(anchor="w", padx=16, pady=(0, 12))
        return value_label
