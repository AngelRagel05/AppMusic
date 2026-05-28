from __future__ import annotations

from abc import ABC, abstractmethod

from music_app.app.domain.entities.song import Song


class SongRepository(ABC):
    @abstractmethod
    def get_by_path(self, path: str) -> Song | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, song: Song) -> Song:
        raise NotImplementedError

