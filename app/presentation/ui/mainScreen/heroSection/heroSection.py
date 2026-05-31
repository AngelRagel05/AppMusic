from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.presentation.styles import applyComponentQss


class HeroSection(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("heroCard")

        self.statusLabel = QLabel("Todo listo para empezar a configurar tu biblioteca.")
        self.statusLabel.setObjectName("statusBanner")
        self.activeFolderValueLabel = QLabel("Sin biblioteca activa")
        self.activeFolderValueLabel.setObjectName("heroMetricValue")
        self.libraryCountValueLabel = QLabel("0 bibliotecas guardadas")
        self.libraryCountValueLabel.setObjectName("heroMetricValue")
        self.activePlaylistValueLabel = QLabel("Sin playlist activa")
        self.activePlaylistValueLabel.setObjectName("heroMetricValue")
        self.playlistCountValueLabel = QLabel("0 playlists guardadas")
        self.playlistCountValueLabel.setObjectName("heroMetricValue")

        title = QLabel("Organiza tu música sin perderte en la interfaz")
        title.setObjectName("heroTitle")
        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setBold(True)
        title.setFont(titleFont)
        title.setWordWrap(True)

        subtitle = QLabel(
            "Empieza definiendo la biblioteca local activa y la playlist principal de "
            "YouTube. Despues ajusta los terminos que la app debe ignorar al comparar nombres."
        )
        subtitle.setObjectName("heroSubtitle")
        subtitle.setWordWrap(True)

        metricsLayout = QHBoxLayout()
        metricsLayout.setSpacing(14)
        metricsLayout.addWidget(self._buildMetricCard("Biblioteca activa", self.activeFolderValueLabel))
        metricsLayout.addWidget(
            self._buildMetricCard("Bibliotecas guardadas", self.libraryCountValueLabel)
        )
        metricsLayout.addWidget(
            self._buildMetricCard("Playlist principal", self.activePlaylistValueLabel)
        )
        metricsLayout.addWidget(
            self._buildMetricCard("Playlists guardadas", self.playlistCountValueLabel)
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(metricsLayout)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    def showStatusMessage(self, message: str) -> None:
        self.statusLabel.setText(message)

    def showLibraryCount(self, count: int) -> None:
        self.libraryCountValueLabel.setText(f"{count} bibliotecas guardadas")

    def showActiveFolderName(self, display_name: str) -> None:
        self.activeFolderValueLabel.setText(display_name)

    def showPlaylistCount(self, count: int) -> None:
        self.playlistCountValueLabel.setText(f"{count} playlists guardadas")

    def showActivePlaylistTitle(self, title: str) -> None:
        self.activePlaylistValueLabel.setText(title)

    def _buildMetricCard(self, title: str, valueLabel: QLabel) -> QWidget:
        card = QFrame()
        card.setObjectName("metricCard")
        titleLabel = QLabel(title)
        titleLabel.setObjectName("heroMetricTitle")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)
        layout.addWidget(titleLabel)
        layout.addWidget(valueLabel)
        card.setLayout(layout)
        return card
