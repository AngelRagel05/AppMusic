from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.library.entities.localSong import LocalSong


class LocalSongRepository(ABC):
    @abstractmethod
    def list_by_folder(self, local_folder_id: int) -> list[LocalSong]:
        raise NotImplementedError

    @abstractmethod
    def get_by_file_path(self, file_path: str) -> LocalSong | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, local_song: LocalSong) -> LocalSong:
        raise NotImplementedError
