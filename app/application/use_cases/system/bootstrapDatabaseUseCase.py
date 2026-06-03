from __future__ import annotations

from typing import Protocol


class DatabaseBootstrapper(Protocol):
    def bootstrap(self) -> None: ...


class BootstrapDatabaseUseCase:
    def __init__(self, bootstrapper: DatabaseBootstrapper) -> None:
        self._bootstrapper = bootstrapper

    def execute(self) -> None:
        self._bootstrapper.bootstrap()
