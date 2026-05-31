from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.styles import applyComponentQss
from app.presentation.ui.shared.dataTable import configureDataTable


class YoutubePlaylistsSection(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("youtubePlaylistsRoot")

        self.activePlaylistLabel = QLabel("Todavia no has elegido una playlist principal.")
        self.activePlaylistLabel.setWordWrap(True)
        self.savedPlaylistsCaption = QLabel(
            "Guarda varias playlists y activa la que quieras comparar con tu musica local."
        )
        self.savedPlaylistsCaption.setObjectName("sectionHint")
        self.playlistUrlInput = QLineEdit()
        self.playlistUrlInput.setPlaceholderText(
            "Ejemplo: https://www.youtube.com/playlist?list=PL1234567890"
        )
        self.savePlaylistButton = QPushButton("Guardar como playlist principal")
        self.savePlaylistButton.setObjectName("primaryButton")
        self.activatePlaylistButton = QPushButton("Activar playlist seleccionada")
        self.activatePlaylistButton.setObjectName("secondaryButton")

        self.playlistsTable = QTableWidget(0, 4)
        self.playlistsTable.setHorizontalHeaderLabels(
            ["Playlist", "Playlist ID", "URL", "Activa"]
        )
        configureDataTable(self.playlistsTable)
        self.playlistsTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.playlistsTable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.playlistsTable.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.playlistsTable.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(18)
        layout.addWidget(self._buildHeader())
        layout.addWidget(self._buildActivePanel())
        layout.addWidget(self._buildForm())
        layout.addLayout(self._buildTableActions())
        layout.addWidget(self.playlistsTable)
        self.setLayout(layout)
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    def showPlaylists(self, youtubePlaylists: list[YoutubePlaylistDto]) -> None:
        self.playlistsTable.setRowCount(len(youtubePlaylists))

        for row_index, youtube_playlist in enumerate(youtubePlaylists):
            self._set_table_item(row_index, 0, youtube_playlist.title)
            self._set_table_item(row_index, 1, youtube_playlist.external_playlist_id)
            self._set_table_item(row_index, 2, youtube_playlist.playlist_url)
            self._set_table_item(row_index, 3, "Si" if youtube_playlist.is_active else "No")

            title_item = self.playlistsTable.item(row_index, 0)
            if title_item is not None:
                title_item.setData(Qt.ItemDataRole.UserRole, youtube_playlist.id)

    def showActivePlaylist(self, activePlaylist: YoutubePlaylistDto | None) -> None:
        if activePlaylist is None:
            self.activePlaylistLabel.setText(
                "Todavia no has elegido una playlist principal. Guarda una URL de YouTube "
                "o activa una ya existente."
            )
            return

        self.activePlaylistLabel.setText(
            f"<b>{activePlaylist.title}</b><br>{activePlaylist.playlist_url}"
        )
        self.playlistUrlInput.setText(activePlaylist.playlist_url)

    def playlistUrl(self) -> str:
        return self.playlistUrlInput.text()

    def setPlaylistUrl(self, playlist_url: str) -> None:
        self.playlistUrlInput.setText(playlist_url)

    def selectedPlaylistId(self) -> int | None:
        selected_items = self.playlistsTable.selectedItems()
        if not selected_items:
            return None

        selected_row = selected_items[0].row()
        playlist_item = self.playlistsTable.item(selected_row, 0)
        if playlist_item is None:
            return None

        playlist_id = playlist_item.data(Qt.ItemDataRole.UserRole)
        if playlist_id is None:
            return None

        return int(playlist_id)

    def _buildHeader(self) -> QWidget:
        container = QWidget()
        title = QLabel("Playlists de YouTube")
        title.setObjectName("sectionTitle")
        intro = QLabel(
            "Define la playlist principal de YouTube que quieres usar como referencia "
            "para comparar tu musica local."
        )
        intro.setObjectName("sectionHint")
        intro.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(intro)
        container.setLayout(layout)
        return container

    def _buildActivePanel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("infoPanel")
        title = QLabel("Playlist principal activa")
        title.setObjectName("panelTitle")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.activePlaylistLabel)
        panel.setLayout(layout)
        return panel

    def _buildForm(self) -> QWidget:
        form = QGroupBox("Guardar una nueva playlist")
        form.setObjectName("softGroup")
        layout = QFormLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addRow("URL de la playlist", self.playlistUrlInput)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.addWidget(self.savePlaylistButton)
        actions_layout.addStretch()
        layout.addRow("", actions_layout)
        form.setLayout(layout)
        return form

    def _buildTableActions(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.addWidget(self.savedPlaylistsCaption)
        layout.addStretch()
        layout.addWidget(self.activatePlaylistButton)
        return layout

    def _set_table_item(self, row_index: int, column_index: int, value: str) -> None:
        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.playlistsTable.setItem(row_index, column_index, item)
