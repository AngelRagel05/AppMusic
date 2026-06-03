from __future__ import annotations

import customtkinter as ctk

from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.styles import (
    ActionButton,
    Signal,
    bindRecursive,
    clearChildren,
    createEntry,
    createFrame,
    createLabel,
    createScrollableFrame,
    setStatusLabelTone,
)
from app.presentation.widgets.statusBadge.statusBadge import StatusBadge


class _YoutubePlaylistRow(ctk.CTkFrame):
    def __init__(self, parent, youtube_playlist: YoutubePlaylistDto, theme) -> None:
        self._theme = theme
        super().__init__(
            parent,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_lg"]),
            border_width=1,
            border_color=self._theme["border"],
        )
        self.activated = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._youtube_playlist_id = youtube_playlist.id

        self.grid_columnconfigure(0, weight=1)

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        content.grid_columnconfigure(0, weight=1)

        createLabel(
            content,
            youtube_playlist.title,
            theme=self._theme,
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")
        createLabel(
            content,
            youtube_playlist.playlist_url,
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=620,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        badgeTone = "success" if youtube_playlist.is_active else "idle"
        badgeText = "Activa" if youtube_playlist.is_active else "Guardada"
        self._statusBadge = StatusBadge(content, badgeText, badgeTone, self._theme)
        self._statusBadge.grid(row=0, column=1, sticky="e", padx=(16, 0))

        actions = createFrame(self, theme=self._theme, fg_color="transparent")
        actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))

        activateButton = ActionButton(actions, "Activar", variant="ghost", theme=self._theme)
        activateButton.clicked.connect(lambda: self.activated.emit(self._youtube_playlist_id))
        activateButton.widget.pack(side="left")

        editButton = ActionButton(actions, "Editar", variant="secondary", theme=self._theme)
        editButton.clicked.connect(lambda: self.editRequested.emit(self._youtube_playlist_id))
        editButton.widget.pack(side="left", padx=(10, 10))

        deleteButton = ActionButton(actions, "Eliminar", variant="danger", theme=self._theme)
        deleteButton.clicked.connect(lambda: self.deleteRequested.emit(self._youtube_playlist_id))
        deleteButton.widget.pack(side="left")

        bindRecursive(self, "<Double-Button-1>", self._emit_activate)

    def _emit_activate(self, _event) -> None:
        self.activated.emit(self._youtube_playlist_id)


class YoutubePlaylistsSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.activateRequested = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()

        topGrid = createFrame(self, theme=self._theme, fg_color="transparent")
        topGrid.pack(fill="x")
        topGrid.grid_columnconfigure(0, weight=1)
        topGrid.grid_columnconfigure(1, weight=1)

        self._buildStatusCard(topGrid).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._buildComposerCard(topGrid).grid(row=0, column=1, sticky="nsew")

        self.statusLabel = createLabel(
            self,
            "Selecciona una playlist para activarla o actualizarla.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
        )
        self.statusLabel.pack(anchor="w", pady=(18, 12))

        listHeader = createFrame(self, theme=self._theme, fg_color="transparent")
        listHeader.pack(fill="x", pady=(8, 12))
        createLabel(
            listHeader,
            "Playlists guardadas",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")

        self._rowsHost = createScrollableFrame(self, theme=self._theme, fg_color="transparent")
        self._rowsHost.pack(fill="both", expand=True)

    def showPlaylists(self, youtube_playlists: list[YoutubePlaylistDto]) -> None:
        clearChildren(self._rowsHost)
        if not youtube_playlists:
            self._buildEmptyState(self._rowsHost).pack(fill="x")
            return

        for youtube_playlist in youtube_playlists:
            row = _YoutubePlaylistRow(self._rowsHost, youtube_playlist, self._theme)
            row.activated.connect(self.activateRequested.emit)
            row.editRequested.connect(self.editRequested.emit)
            row.deleteRequested.connect(self.deleteRequested.emit)
            row.pack(fill="x", pady=(0, 14))

    def showActivePlaylist(self, active_playlist: YoutubePlaylistDto | None) -> None:
        if active_playlist is None:
            self.activePlaylistValue.configure(text="Sin playlist configurada")
            self.activePlaylistMeta.configure(text="Aún no hay una playlist principal de referencia.")
            self.activePlaylistUrl.configure(text="Añade una URL para empezar a sincronizar tu música.")
            self.activePlaylistBadge.setStatus("Pendiente", "idle")
            return

        self.activePlaylistValue.configure(text=active_playlist.title)
        self.activePlaylistMeta.configure(text="Playlist preparada para comparaciones y sincronización.")
        self.activePlaylistUrl.configure(text=active_playlist.playlist_url)
        self.activePlaylistBadge.setStatus("Activa", "success")
        self.setPlaylistTitle(active_playlist.title)
        self.setPlaylistUrl(active_playlist.playlist_url)

    def playlistTitle(self) -> str:
        return self.playlistTitleInput.get()

    def playlistUrl(self) -> str:
        return self.playlistUrlInput.get()

    def setPlaylistTitle(self, title: str) -> None:
        self.playlistTitleInput.delete(0, "end")
        self.playlistTitleInput.insert(0, title)

    def setPlaylistUrl(self, playlist_url: str) -> None:
        self.playlistUrlInput.delete(0, "end")
        self.playlistUrlInput.insert(0, playlist_url)

    def setSaveMode(self, is_editing: bool) -> None:
        if is_editing:
            self.savePlaylistButton.setText("Guardar cambios")
            self.formHelper.configure(
                text="Estás editando la playlist seleccionada. Guarda para actualizar la referencia principal."
            )
            return

        self.savePlaylistButton.setText("Guardar playlist")
        self.formHelper.configure(
            text="Define una playlist principal para sincronizar y comparar contra tu biblioteca local."
        )

    def clearForm(self) -> None:
        self.playlistTitleInput.delete(0, "end")
        self.playlistUrlInput.delete(0, "end")
        self.setSaveMode(False)

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.statusLabel.configure(text=message)
        setStatusLabelTone(self.statusLabel, tone, theme=self._theme)

    def focusPrimaryInput(self) -> None:
        self.playlistTitleInput.focus_set()

    def _buildStatusCard(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Playlist principal",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 10))

        headerRow = createFrame(card, theme=self._theme, fg_color="transparent")
        headerRow.pack(fill="x", padx=20)
        self.activePlaylistValue = createLabel(
            headerRow,
            "Sin playlist configurada",
            theme=self._theme,
            font=("Segoe UI", 20, "bold"),
            wraplength=360,
        )
        self.activePlaylistValue.pack(side="left", anchor="w")
        self.activePlaylistBadge = StatusBadge(headerRow, "Pendiente", "idle", self._theme)
        self.activePlaylistBadge.pack(side="right")

        self.activePlaylistMeta = createLabel(
            card,
            "Aún no hay una playlist principal de referencia.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=380,
        )
        self.activePlaylistMeta.pack(anchor="w", padx=20, pady=(12, 6))
        self.activePlaylistUrl = createLabel(
            card,
            "Añade una URL para empezar a sincronizar tu música.",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12),
            wraplength=380,
        )
        self.activePlaylistUrl.pack(anchor="w", padx=20, pady=(0, 18))
        return card

    def _buildComposerCard(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Configurar playlist",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 10))
        self.formHelper = createLabel(
            card,
            "Define una playlist principal para sincronizar y comparar contra tu biblioteca local.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=380,
        )
        self.formHelper.pack(anchor="w", padx=20, pady=(0, 14))

        self.playlistTitleInput = createEntry(
            card,
            theme=self._theme,
            width=420,
            placeholder_text="Nombre visible de la playlist",
        )
        self.playlistTitleInput.pack(fill="x", padx=20)
        self.playlistUrlInput = createEntry(
            card,
            theme=self._theme,
            width=420,
            placeholder_text="https://www.youtube.com/playlist?list=...",
        )
        self.playlistUrlInput.pack(fill="x", padx=20, pady=(12, 0))

        actions = createFrame(card, theme=self._theme, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(16, 20))
        self.savePlaylistButton = ActionButton(actions, "Guardar playlist", theme=self._theme)
        self.savePlaylistButton.widget.pack(side="right")
        return card

    def _buildEmptyState(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Todavía no hay playlists guardadas",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 8))
        createLabel(
            card,
            "Guarda tu primera playlist principal para usarla como referencia de comparación y sincronización.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=760,
        ).pack(anchor="w", padx=20, pady=(0, 18))
        return card
