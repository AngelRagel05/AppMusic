from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.localFolder import LocalFolder


class LocalFolderRepository(ABC):
    @abstractmethod
    def get_active(self) -> LocalFolder | None:
        raise NotImplementedError

    @abstractmethod
    def save_as_active(self, path: str, display_name: str) -> LocalFolder:
        raise NotImplementedError
