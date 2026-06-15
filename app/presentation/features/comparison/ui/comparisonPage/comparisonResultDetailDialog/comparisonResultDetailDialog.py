from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.presentation.styles import createEntry, createOptionMenu
from app.presentation.features.comparison.comparisonResultDetailViewData import (
    ComparisonResultDetailViewData,
)
from app.presentation.styles import ActionButton, createFrame, createLabel, createScrollableFrame
from app.shared.constants.comparison import ComparisonStatus


class ComparisonResultDetailDialog(ctk.CTkFrame):
    LOCAL_SONG_COLUMNS: tuple[tuple[str, str, int, bool], ...] = (
        ("title", "Titulo", 190, True),
        ("artist", "Artista", 160, True),
        ("album", "Album", 140, True),
        ("duration", "Dur.", 56, False),
        ("file", "Archivo", 180, True),
    )

    def __init__(
        self,
        parent,
        theme,
        detail_view_data: ComparisonResultDetailViewData,
        comparison_item: PlaylistComparisonItemResultDto,
        local_songs: list[LocalSongDto],
        *,
        linked_local_song_id: int | None = None,
        on_save_decision: Callable[[str, int | None], bool] | None = None,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        self._theme = theme
        self._onClose = on_close
        self._comparisonItem = comparison_item
        self._onSaveDecision = on_save_decision
        self._isClosing = False
        self._escapeBindingTarget = None
        self._escapeBindingId: str | None = None
        self._allLocalSongs = list(local_songs)
        self._filteredLocalSongs: list[LocalSongDto] = []
        self._linkedLocalSongId = linked_local_song_id
        self._selectedLocalSongId = linked_local_song_id
        self._statusVariable = ctk.StringVar(value=comparison_item.comparison_status.value)
        super().__init__(parent, fg_color="#0E1117", corner_radius=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.bind("<Button-1>", lambda _event: self._close())
        self._buildLayout(detail_view_data)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self.focus_force()
        self._bindEscapeShortcut()

    def _buildLayout(self, detail_view_data: ComparisonResultDetailViewData) -> None:
        shell = createFrame(self, theme=self._theme, fg_color="transparent")
        shell.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        shell.grid_rowconfigure(0, weight=1)
        shell.grid_columnconfigure(0, weight=1)

        modal = createFrame(
            shell,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_md"]),
        )
        modal.grid(row=0, column=0)
        modal.grid_rowconfigure(1, weight=1)
        modal.grid_columnconfigure(0, weight=1)
        modal.grid_propagate(False)
        modal.configure(width=740, height=500)
        modal.bind("<Button-1>", lambda _event: "break")

        header = createFrame(modal, theme=self._theme, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 8))
        header.grid_columnconfigure(0, weight=1)
        header.bind("<Button-1>", lambda _event: "break")
        createLabel(
            header,
            "Detalle del resultado",
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")
        close_button = ctk.CTkButton(
            header,
            text="X",
            width=28,
            height=28,
            corner_radius=int(self._theme["radius_sm"]),
            fg_color=self._theme["surface"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            border_width=0,
            font=("Segoe UI", 10, "bold"),
            command=self._close,
        )
        close_button.grid(row=0, column=1, sticky="e")

        content = createScrollableFrame(
            modal,
            theme=self._theme,
            fg_color=self._theme["surface"],
            corner_radius=int(self._theme["radius_sm"]),
        )
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        content.grid_columnconfigure(0, minsize=140, weight=0)
        content.grid_columnconfigure(1, weight=1)
        content.bind("<Button-1>", lambda _event: "break")

        self._addField(content, 0, "Estado", detail_view_data.status_label, is_badge=True)
        self._addField(content, 1, "Titulo playlist", detail_view_data.title)
        self._addField(content, 2, "Artista playlist", detail_view_data.subtitle)
        self._addField(content, 3, "Coincidencia local", detail_view_data.local_match)
        self._addField(content, 4, "Score", detail_view_data.score_label)
        self._addField(content, 5, "Revision", detail_view_data.review_note)
        self._addField(content, 6, "Disponibilidad", detail_view_data.availability_summary)
        self._addField(content, 7, "Motivo detectado", detail_view_data.reason_summary)
        self._addField(content, 8, "Detalle", detail_view_data.raw_reason, multiline=True)
        self._addField(content, 9, "Local enlazada", detail_view_data.linked_song_title)
        self._addField(content, 10, "Ruta o detalle", detail_view_data.linked_song_detail, multiline=True)
        self._buildManualDecisionEditor(content, start_row=11)

        footer = createFrame(modal, theme=self._theme, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="e", padx=12, pady=(0, 10))
        footer.bind("<Button-1>", lambda _event: "break")
        self._saveAction = ActionButton(
            footer,
            text="Guardar",
            variant="primary",
            theme=self._theme,
            height=30,
        )
        self._saveAction.widget.configure(width=120, font=("Segoe UI", 10, "bold"))
        self._saveAction.clicked.connect(self._handleSaveRequested)
        self._saveAction.widget.pack(side="right", padx=(0, 8))
        close_action = ActionButton(
            footer,
            text="Cerrar",
            variant="secondary",
            theme=self._theme,
            height=30,
        )
        close_action.widget.configure(width=110, font=("Segoe UI", 10, "bold"))
        close_action.clicked.connect(self._close)
        close_action.widget.pack(side="right")
        self._refreshEditorState()

    def _addField(
        self,
        parent,
        row: int,
        label: str,
        value: str,
        *,
        is_badge: bool = False,
        multiline: bool = False,
    ) -> None:
        createLabel(
            parent,
            f"{label}:",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=row, column=0, sticky="nw", padx=(10, 10), pady=(8 if row == 0 else 5, 0))
        if is_badge:
            badge = createFrame(
                parent,
                theme=self._theme,
                fg_color=self._theme["accent_soft"],
                corner_radius=int(self._theme["radius_sm"]),
            )
            badge.grid(row=row, column=1, sticky="w", pady=(8 if row == 0 else 5, 0))
            createLabel(
                badge,
                value.upper(),
                theme=self._theme,
                text_color=self._theme["text"],
                font=("Segoe UI", 9, "bold"),
                anchor="center",
                justify="center",
            ).pack(padx=7, pady=3)
            return

        createLabel(
            parent,
            value,
            theme=self._theme,
            text_color=self._theme["text"] if not multiline else self._theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=460 if multiline else 0,
            justify="left",
        ).grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=(8 if row == 0 else 5, 0),
        )

    def _buildManualDecisionEditor(self, parent, *, start_row: int) -> None:
        section = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_sm"]),
        )
        section.grid(
            row=start_row,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(12, 6),
        )
        section.grid_columnconfigure(0, weight=1)
        section.bind("<Button-1>", lambda _event: "break")

        createLabel(
            section,
            "Edicion manual",
            theme=self._theme,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        createLabel(
            section,
            "Ajusta el estado final y, si hace falta, elige o quita la cancion local enlazada.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
            wraplength=620,
        ).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        controls = createFrame(section, theme=self._theme, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        controls.grid_columnconfigure(1, weight=1)
        createLabel(
            controls,
            "Estado",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self._statusMenu = createOptionMenu(
            controls,
            self._statusVariable,
            values=[
                ComparisonStatus.FOUND.value,
                ComparisonStatus.MISSING.value,
                ComparisonStatus.POSSIBLE_MATCH.value,
            ],
            theme=self._theme,
            width=160,
        )
        self._statusMenu.configure(font=("Segoe UI", 10), height=30)
        self._statusMenu.configure(command=self._handleStatusChanged)
        self._statusMenu.grid(row=0, column=1, sticky="w")

        link_actions = createFrame(section, theme=self._theme, fg_color="transparent")
        link_actions.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._selectedLocalSongLabel = createLabel(
            link_actions,
            "",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        self._selectedLocalSongLabel.pack(side="left")
        self._clearLinkButton = ctk.CTkButton(
            link_actions,
            text="Quitar enlace local",
            height=28,
            width=132,
            corner_radius=int(self._theme["radius_sm"]),
            fg_color=self._theme["surface"],
            hover_color=self._theme["hover"],
            text_color=self._theme["text_secondary"],
            border_width=0,
            font=("Segoe UI", 10),
            command=self._handleClearLinkRequested,
        )
        self._clearLinkButton.pack(side="right")

        self._localSongSearchVariable = ctk.StringVar(value="")
        self._localSongSearchEntry = createEntry(
            section,
            theme=self._theme,
            width=420,
            placeholder_text="Buscar cancion local por titulo, artista, album o archivo...",
            textvariable=self._localSongSearchVariable,
        )
        self._localSongSearchEntry.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._localSongSearchEntry.configure(height=30, font=("Segoe UI", 11))
        self._localSongSearchVariable.trace_add(
            "write",
            lambda *_args: self._applyLocalSongQuery(),
        )

        self._localSongEmptyState = createLabel(
            section,
            "Escribe al menos 2 caracteres para buscar canciones locales.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        self._localSongEmptyState.grid(row=5, column=0, sticky="w", padx=8, pady=(0, 8))

        self._localSongTableContainer = createFrame(section, theme=self._theme, fg_color="transparent")
        self._localSongTableContainer.grid(row=6, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._localSongTableContainer.grid_rowconfigure(0, weight=1)
        self._localSongTableContainer.grid_columnconfigure(0, weight=1)

        self._configureLocalSongTreeStyle()
        self._buildLocalSongTree()
        self._renderLocalSongRows()

    def _configureLocalSongTreeStyle(self) -> None:
        self._localSongTreeStyleName = f"comparisonLocalSongs{hex(id(self))}.Treeview"
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            self._localSongTreeStyleName,
            background=self._theme["surface"],
            fieldbackground=self._theme["surface"],
            foreground=self._theme["text"],
            borderwidth=0,
            relief="flat",
            rowheight=28,
            font=("Segoe UI", 10),
        )
        style.configure(
            f"{self._localSongTreeStyleName}.Heading",
            background=self._theme["panel"],
            foreground=self._theme["text_muted"],
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=(6, 5),
        )
        style.map(
            self._localSongTreeStyleName,
            background=[("selected", self._theme["accent_soft"])],
            foreground=[("selected", self._theme["text"])],
        )

    def _buildLocalSongTree(self) -> None:
        columns = [column_key for column_key, _title, _width, _stretch in self.LOCAL_SONG_COLUMNS]
        self._localSongTree = ttk.Treeview(
            self._localSongTableContainer,
            columns=columns,
            show="headings",
            style=self._localSongTreeStyleName,
            selectmode="browse",
            height=6,
        )
        self._localSongTree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            self._localSongTableContainer,
            orient="vertical",
            command=self._localSongTree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._localSongTree.configure(yscrollcommand=scrollbar.set)

        for column_key, title, width, stretch in self.LOCAL_SONG_COLUMNS:
            anchor = tk.E if column_key == "duration" else tk.W
            self._localSongTree.heading(column_key, text=title, anchor=anchor)
            self._localSongTree.column(
                column_key,
                anchor=anchor,
                width=width,
                minwidth=width,
                stretch=stretch,
            )

        self._localSongTree.bind("<<TreeviewSelect>>", self._handleLocalSongSelectionChanged)
        self._localSongTree.bind("<Double-1>", lambda _event: self._handleConfirmLinkRequested())

    def _applyLocalSongQuery(self) -> None:
        query = " ".join(self._localSongSearchVariable.get().lower().split())
        selected_song = self._findLocalSongById(self._selectedLocalSongId)
        if len(query) < 2:
            self._filteredLocalSongs = [selected_song] if selected_song is not None else []
        else:
            self._filteredLocalSongs = [
                local_song
                for local_song in self._allLocalSongs
                if query in self._buildLocalSongSearchText(local_song)
            ]
            if (
                selected_song is not None
                and selected_song.id not in {song.id for song in self._filteredLocalSongs}
            ):
                self._filteredLocalSongs.insert(0, selected_song)
        self._renderLocalSongRows()

    def _renderLocalSongRows(self) -> None:
        for item_id in self._localSongTree.get_children():
            self._localSongTree.delete(item_id)

        if not self._filteredLocalSongs:
            self._localSongTableContainer.grid_remove()
            self._localSongEmptyState.grid()
            self._localSongEmptyState.configure(text=self._buildEmptySearchMessage())
            self._refreshEditorState()
            return

        self._localSongEmptyState.grid_remove()
        self._localSongTableContainer.grid()
        for local_song in self._filteredLocalSongs:
            self._localSongTree.insert(
                "",
                "end",
                iid=str(local_song.id),
                values=(
                    local_song.title or local_song.file_name,
                    local_song.artist or "Artista desconocido",
                    local_song.album or "-",
                    self._formatDuration(local_song.duration_seconds),
                    local_song.file_name,
                ),
            )

        selected_id = self._selectedLocalSongId or self._linkedLocalSongId
        if selected_id is not None and self._localSongTree.exists(str(selected_id)):
            self._localSongTree.selection_set(str(selected_id))
            self._localSongTree.focus(str(selected_id))
            self._localSongTree.see(str(selected_id))
        self._refreshEditorState()

    def _buildLocalSongSearchText(self, local_song: LocalSongDto) -> str:
        return " ".join(
            part.strip().lower()
            for part in (
                local_song.title,
                local_song.artist,
                local_song.album,
                local_song.file_name,
                local_song.file_path,
            )
            if part
        )

    def _formatDuration(self, duration_seconds: float) -> str:
        total_seconds = max(int(round(duration_seconds or 0.0)), 0)
        return f"{total_seconds // 60}:{total_seconds % 60:02d}"

    def _handleLocalSongSelectionChanged(self, _event) -> None:
        selected_items = self._localSongTree.selection()
        if not selected_items:
            self._selectedLocalSongId = None
        else:
            self._selectedLocalSongId = int(selected_items[0])
        self._refreshEditorState()

    def _refreshEditorState(self) -> None:
        if not hasattr(self, "_saveAction"):
            return
        selected_song = self._findLocalSongById(self._selectedLocalSongId)
        if selected_song is None:
            self._selectedLocalSongLabel.configure(text="Sin cancion local seleccionada")
        else:
            self._selectedLocalSongLabel.configure(
                text=(
                    f'Seleccion actual: {selected_song.title or selected_song.file_name} · '
                    f'{selected_song.artist or "Artista desconocido"}'
                )
            )

        normalized_status = ComparisonStatus(self._statusVariable.get())
        selector_enabled = normalized_status is not ComparisonStatus.MISSING
        search_state = "normal" if selector_enabled else "disabled"
        button_state = "normal" if selector_enabled else "disabled"
        self._statusMenu.configure(state="normal")
        self._clearLinkButton.configure(state=button_state)
        self._localSongSearchEntry.configure(state=search_state)
        self._localSongTree.configure(selectmode="browse" if selector_enabled else "none")
        if not selector_enabled:
            self._localSongTree.selection_remove(self._localSongTree.selection())
            self._localSongEmptyState.configure(
                text="Estado missing seleccionado. El enlace local se eliminara al guardar."
            )
        elif not self._filteredLocalSongs:
            self._localSongEmptyState.configure(text=self._buildEmptySearchMessage())

        can_save = True
        if normalized_status is ComparisonStatus.FOUND and self._selectedLocalSongId is None:
            can_save = False
        if self._onSaveDecision is None:
            can_save = False
        self._saveAction.widget.configure(state="normal" if can_save else "disabled")

    def _handleStatusChanged(self, selected_status: str) -> None:
        normalized_status = ComparisonStatus(selected_status)
        if normalized_status is ComparisonStatus.MISSING:
            self._selectedLocalSongId = None
            self._localSongTree.selection_remove(self._localSongTree.selection())
        self._applyLocalSongQuery()
        self._refreshEditorState()

    def _handleClearLinkRequested(self) -> None:
        self._selectedLocalSongId = None
        self._localSongTree.selection_remove(self._localSongTree.selection())
        self._applyLocalSongQuery()
        self._refreshEditorState()

    def _handleSaveRequested(self) -> None:
        if self._onSaveDecision is None:
            return
        normalized_status = ComparisonStatus(self._statusVariable.get())
        local_song_id = (
            None if normalized_status is ComparisonStatus.MISSING else self._selectedLocalSongId
        )
        if self._onSaveDecision(normalized_status.value, local_song_id):
            self._close()

    def _findLocalSongById(self, local_song_id: int | None) -> LocalSongDto | None:
        if local_song_id is None:
            return None
        for local_song in self._allLocalSongs:
            if local_song.id == local_song_id:
                return local_song
        return None

    def _buildEmptySearchMessage(self) -> str:
        query = " ".join(self._localSongSearchVariable.get().split())
        if len(query) < 2:
            return "Escribe al menos 2 caracteres para buscar canciones locales."
        return "No hay canciones locales que coincidan con la busqueda."

    def _handleEscape(self, _event) -> None:
        self._close()

    def _bindEscapeShortcut(self) -> None:
        self._escapeBindingTarget = self.winfo_toplevel()
        self._escapeBindingId = self._escapeBindingTarget.bind(
            "<Escape>",
            self._handleEscape,
            add="+",
        )

    def _close(self) -> None:
        if self._isClosing:
            return
        self._isClosing = True
        if self._escapeBindingTarget is not None and self._escapeBindingId is not None:
            self._escapeBindingTarget.unbind("<Escape>", self._escapeBindingId)
            self._escapeBindingTarget = None
            self._escapeBindingId = None
        if self._onClose is not None:
            self._onClose()
        self.destroy()
