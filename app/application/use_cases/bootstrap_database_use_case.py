from __future__ import annotations

from app.infrastructure.database.bootstrap import DatabaseBootstrapper


class BootstrapDatabaseUseCase:
    def __init__(self, bootstrapper: DatabaseBootstrapper) -> None:
        self._bootstrapper = bootstrapper

    def execute(self) -> None:
        self._bootstrapper.bootstrap()
