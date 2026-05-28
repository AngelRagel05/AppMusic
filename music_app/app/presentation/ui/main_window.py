from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from music_app.app.application.use_cases.scan_music_folder import ScanMusicFolderUseCase
from music_app.app.infrastructure.database.session import get_session
from music_app.app.infrastructure.filesystem.music_scanner import MusicScanner
from music_app.app.infrastructure.metadata.reader import MetadataReader
from music_app.app.infrastructure.repositories.song_repository import SqlAlchemySongRepository


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music App")
        self.resize(900, 600)

        self._status_label = QLabel("Selecciona una carpeta para escanear musica MP3.")
        self._scan_button = QPushButton("Escanear carpeta")
        self._scan_button.clicked.connect(self._scan_music_folder)

        layout = QVBoxLayout()
        layout.addWidget(self._status_label)
        layout.addWidget(self._scan_button)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _scan_music_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Selecciona una carpeta de musica")
        if not folder:
            return

        session = get_session()
        try:
            use_case = ScanMusicFolderUseCase(
                song_repository=SqlAlchemySongRepository(session),
                music_scanner=MusicScanner(),
                metadata_reader=MetadataReader(),
            )
            result = use_case.execute(folder)
        finally:
            session.close()

        self._status_label.setText(
            f"Escaneados: {result.scanned_files} | Importados: {result.imported_songs} | "
            f"Omitidos: {result.skipped_existing}"
        )
        QMessageBox.information(
            self,
            "Escaneo completado",
            f"Carpeta: {Path(folder).name}\n"
            f"Escaneados: {result.scanned_files}\n"
            f"Importados: {result.imported_songs}\n"
            f"Omitidos: {result.skipped_existing}",
        )

