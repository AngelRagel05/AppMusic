from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPlayer:
    def __init__(self) -> None:
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

    def play_file(self, path: str) -> None:
        self._player.setSource(QUrl.fromLocalFile(str(Path(path).resolve())))
        self._player.play()

    def stop(self) -> None:
        self._player.stop()

