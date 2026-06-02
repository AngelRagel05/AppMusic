from __future__ import annotations

import tkinter as tk

from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.uiTheme import (
    ActionButton,
    Signal,
    bindRecursive,
    clearChildren,
    createEntry,
    createLabel,
    setStatusLabelTone,
)
from app.presentation.uiTheme.themePalette import ThemeTokens


class _YoutubePlaylistRow(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        youtube_playlist: YoutubePlaylistDto,
        theme: ThemeTokens,
    ) -> None:
        super().__init__(parent, bg=theme["surface"], padx=16, pady=14, cursor="hand2")
        self.activated = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._youtube_playlist_id = youtube_playlist.id
        self._theme = theme

        text_host = tk.Frame(self, bg=self._theme["surface"])
        text_host.pack(side="left", fill="both", expand=True)

        createLabel(
            text_host,
            youtube_playlist.title,
            theme=self._theme,
            bg=self._theme["surface"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        createLabel(
            text_host,
            f"ID YouTube: {youtube_playlist.external_playlist_id}",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_secondary"],
        ).pack(anchor="w", pady=(4, 0))
        createLabel(
            text_host,
            "Playlist lista para sincronizar",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        status = createLabel(
            self,
            "Activa" if youtube_playlist.is_active else "Guardada",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["success"]
            if youtube_playlist.is_active
            else self._theme["text_secondary"],
            font=("Segoe UI", 9, "bold"),
        )
        status.pack(side="left", padx=(12, 12), anchor="n")

        menu_button = tk.Menubutton(
            self,
            text="...",
            bg=self._theme["surface_alt"],
            fg=self._theme["text"],
            activebackground=self._theme["surface"],
            activeforeground=self._theme["text"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        menu = tk.Menu(
            menu_button,
            tearoff=0,
            bg=self._theme["surface_alt"],
            fg=self._theme["text"],
        )
        menu.add_command(
            label="Editar",
            command=lambda: self.editRequested.emit(self._youtube_playlist_id),
        )
        menu.add_command(
            label="Eliminar",
            command=lambda: self.deleteRequested.emit(self._youtube_playlist_id),
        )
        menu_button.configure(menu=menu)
        menu_button.pack(side="left", anchor="n")

        bindRecursive(self, "<Double-Button-1>", self._emit_activate)

    def _emit_activate(self, _event) -> None:
        self.activated.emit(self._youtube_playlist_id)


class YoutubePlaylistsSection(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["bg"])
        self.activateRequested = Signal()
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._theme = theme

        self.activePlaylistValue = createLabel(
            self,
            "Sin playlist principal",
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        )
        self.activePlaylistSongs = createLabel(
            self,
            "Canciones sin sincronizar",
            theme=self._theme,
            fg=self._theme["text_secondary"],
        )
        self.activePlaylistUrl = createLabel(
            self,
            "URL pendiente",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            wraplength=720,
        )

        self.playlistTitleInput = createEntry(self, theme=self._theme, width=28)
        self.playlistUrlInput = createEntry(self, theme=self._theme, width=60)
        self.savePlaylistButton = ActionButton(self, "Guardar playlist", theme=self._theme)
        self.saveModeLabel = createLabel(
            self,
            "Crea o actualiza la playlist principal desde aqui.",
            theme=self._theme,
            fg=self._theme["text_secondary"],
        )
        self.statusLabel = createLabel(
            self,
            "Doble clic en una playlist para activarla.",
            theme=self._theme,
            fg=self._theme["accent"],
            wraplength=720,
        )
        self.listCaption = createLabel(
            self,
            "Playlists guardadas",
            theme=self._theme,
            font=("Segoe UI", 11, "bold"),
        )

        self._rowsHost = tk.Frame(self, bg=self._theme["bg"])

        self._buildComposerCard().pack(fill="x")
        self.saveModeLabel.pack(anchor="w", pady=(16, 4))
        self.statusLabel.pack(anchor="w")
        self.listCaption.pack(anchor="w", pady=(16, 8))
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
            row.pack(fill="x", pady=(0, 12))

    def showActivePlaylist(self, active_playlist: YoutubePlaylistDto | None) -> None:
        if active_playlist is None:
            self.activePlaylistValue.configure(text="Sin playlist principal")
            self.activePlaylistSongs.configure(text="Canciones sin sincronizar")
            self.activePlaylistUrl.configure(text="URL pendiente")
            return

        self.activePlaylistValue.configure(text=active_playlist.title)
        self.activePlaylistSongs.configure(
            text=f"ID YouTube: {active_playlist.external_playlist_id}"
        )
        self.activePlaylistUrl.configure(text=active_playlist.playlist_url)
        self.setPlaylistTitle(active_playlist.title)
        self.setPlaylistUrl(active_playlist.playlist_url)

    def playlistTitle(self) -> str:
        return self.playlistTitleInput.get()

    def playlistUrl(self) -> str:
        return self.playlistUrlInput.get()

    def setPlaylistTitle(self, title: str) -> None:
        self.playlistTitleInput.delete(0, tk.END)
        self.playlistTitleInput.insert(0, title)

    def setPlaylistUrl(self, playlist_url: str) -> None:
        self.playlistUrlInput.delete(0, tk.END)
        self.playlistUrlInput.insert(0, playlist_url)

    def setSaveMode(self, is_editing: bool) -> None:
        if is_editing:
            self.savePlaylistButton.setText("Guardar playlist")
            self.saveModeLabel.configure(
                text="Estas editando la playlist seleccionada. Guarda para aplicar los cambios."
            )
            return

        self.savePlaylistButton.setText("Guardar playlist")
        self.saveModeLabel.configure(text="Crea o actualiza la playlist principal desde aqui.")

    def clearForm(self) -> None:
        self.playlistTitleInput.delete(0, tk.END)
        self.playlistUrlInput.delete(0, tk.END)
        self.setSaveMode(False)

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.statusLabel.configure(text=message)
        setStatusLabelTone(self.statusLabel, tone, theme=self._theme)

    def focusPrimaryInput(self) -> None:
        self.playlistTitleInput.focus_set()

    def _buildComposerCard(self) -> tk.Frame:
        card = tk.Frame(self, bg=self._theme["surface"], padx=16, pady=16)
        self.activePlaylistValue.configure(bg=self._theme["surface"])
        self.activePlaylistSongs.configure(bg=self._theme["surface"])
        self.activePlaylistUrl.configure(bg=self._theme["surface"])

        self.activePlaylistValue.pack(in_=card, anchor="w")
        self.activePlaylistSongs.pack(in_=card, anchor="w", pady=(2, 0))
        self.activePlaylistUrl.pack(in_=card, anchor="w", pady=(2, 0))

        first_row = tk.Frame(card, bg=self._theme["surface"])
        first_row.pack(fill="x", pady=(14, 0))
        self.playlistTitleInput.pack(in_=first_row, side="left", fill="x", expand=True)
        self.savePlaylistButton.widget.pack(in_=first_row, side="left", padx=(10, 0))
        self.playlistUrlInput.pack(in_=card, fill="x", pady=(12, 0))
        return card

    def _buildEmptyState(self, parent: tk.Misc) -> tk.Frame:
        card = tk.Frame(parent, bg=self._theme["surface"], padx=18, pady=18)
        createLabel(
            card,
            "Todavia no hay playlists guardadas",
            theme=self._theme,
            bg=self._theme["surface"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        createLabel(
            card,
            "Guarda tu primera playlist principal para verla aqui como una referencia musical limpia.",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_secondary"],
            wraplength=700,
        ).pack(anchor="w", pady=(6, 0))
        return card
