from __future__ import annotations

import customtkinter as ctk

from app.presentation.shared.widgets.statCard.statCard import StatCard
from app.presentation.uiTheme import ActionButton, createFrame, createLabel
from app.presentation.uiTheme.themePalette import ThemeTokens


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, theme: ThemeTokens) -> None:
        self._theme = theme
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)

        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")
        self.grid_rowconfigure(3, weight=1)

        self.scanLibraryButton = ActionButton(
            self,
            "Escanear biblioteca",
            theme=self._theme,
        )

        self._build_header().grid(row=0, column=0, columnspan=4, sticky="ew")
        self._build_stats().grid(row=1, column=0, columnspan=4, sticky="ew", pady=(28, 0))
        self._build_bottom_cards().grid(
            row=2, column=0, columnspan=4, sticky="nsew", pady=(28, 0)
        )

    def setActiveFolderName(self, name: str) -> None:
        self.libraryCard.setValue(name)

    def setActivePlaylistTitle(self, title: str) -> None:
        self.playlistCard.setValue(title)

    def setSongCount(self, value: str) -> None:
        self.songsCard.setValue(value)

    def setSyncStatus(self, value: str, tone: str) -> None:
        self.syncCard.setValue(value)
        self.syncCard.setBadge(value, tone)

    def setLastAction(self, value: str) -> None:
        self.lastActionValue.configure(text=value)
        if self.activityLines:
            self.activityLines[0].configure(text=value)

    def _build_header(self):
        header = createFrame(self, theme=self._theme, fg_color="transparent")
        header.grid_columnconfigure(0, weight=1)

        titleGroup = createFrame(header, theme=self._theme, fg_color="transparent")
        titleGroup.grid(row=0, column=0, sticky="w")
        createLabel(
            titleGroup,
            "Resumen",
            theme=self._theme,
            font=("Segoe UI", int(self._theme["title_size"]), "bold"),
        ).pack(anchor="w")
        createLabel(
            titleGroup,
            "Vista general del estado de tu biblioteca musical",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", int(self._theme["subtitle_size"])),
        ).pack(anchor="w", pady=(6, 0))

        self.scanLibraryButton.widget.grid(row=0, column=1, sticky="e")
        return header

    def _build_stats(self):
        stats = createFrame(self, theme=self._theme, fg_color="transparent")
        for column in range(4):
            stats.grid_columnconfigure(column, weight=1, uniform="stats")

        self.libraryCard = StatCard(
            stats,
            "Biblioteca activa",
            "Sin biblioteca configurada",
            self._theme,
        )
        self.playlistCard = StatCard(
            stats,
            "Playlist activa",
            "Sin playlist configurada",
            self._theme,
        )
        self.syncCard = StatCard(
            stats,
            "Estado de sincronización",
            "Pendiente",
            self._theme,
            badge_text="Pendiente",
            badge_tone="idle",
        )
        self.songsCard = StatCard(
            stats,
            "Canciones detectadas",
            "Sin escaneo reciente",
            self._theme,
        )

        cards = (self.libraryCard, self.playlistCard, self.syncCard, self.songsCard)
        for index, card in enumerate(cards):
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 8 if index < 3 else 0))
        return stats

    def _build_bottom_cards(self):
        wrapper = createFrame(self, theme=self._theme, fg_color="transparent")
        wrapper.grid_columnconfigure(0, weight=3)
        wrapper.grid_columnconfigure(1, weight=2)

        lastActionCard = createFrame(
            wrapper,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        lastActionCard.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        createLabel(
            lastActionCard,
            "Última acción",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", int(self._theme["label_size"]), "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 12))
        self.lastActionValue = createLabel(
            lastActionCard,
            "Todavía no hay acciones registradas",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
            wraplength=620,
        )
        self.lastActionValue.pack(anchor="w", padx=20, pady=(0, 18))

        recentActivityCard = createFrame(
            wrapper,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        recentActivityCard.grid(row=0, column=1, sticky="nsew")
        createLabel(
            recentActivityCard,
            "Actividad reciente",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", int(self._theme["label_size"]), "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 12))
        self.activityLines = []
        for text in (
            "La aplicación mostrará aquí cambios de bibliotecas y playlists activas.",
            "Las próximas acciones de escaneo y sincronización quedarán resumidas en este panel.",
        ):
            line = createLabel(
                recentActivityCard,
                text,
                theme=self._theme,
                text_color=self._theme["text_secondary"],
                font=("Segoe UI", 13),
                wraplength=360,
            )
            line.pack(anchor="w", padx=20, pady=(0, 12))
            self.activityLines.append(line)

        return wrapper
