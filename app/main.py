from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.application.use_cases import (
    BootstrapDatabaseUseCase,
    CreateIgnoredTermUseCase,
    DefineMainLocalFolderUseCase,
    GetActiveLocalFolderUseCase,
    ListIgnoredTermsUseCase,
)
from app.config.settings import get_settings
from app.infrastructure.database import DatabaseBootstrapper, SessionLocal, engine, get_session
from app.infrastructure.repositories import (
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
)
from app.presentation.ui.main_window import MainWindow
from app.presentation.viewmodels import IgnoredTermsViewModel, LocalFolderViewModel
from app.utils.logging import configure_logging


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    BootstrapDatabaseUseCase(DatabaseBootstrapper(engine, SessionLocal)).execute()
    session = get_session()

    ignored_term_repository = IgnoredTermSqlAlchemyRepository(session)
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    ignored_terms_view_model = IgnoredTermsViewModel(
        list_use_case=ListIgnoredTermsUseCase(ignored_term_repository),
        create_use_case=CreateIgnoredTermUseCase(ignored_term_repository),
    )
    local_folder_view_model = LocalFolderViewModel(
        get_active_use_case=GetActiveLocalFolderUseCase(local_folder_repository),
        define_main_use_case=DefineMainLocalFolderUseCase(local_folder_repository),
    )

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)

    window = MainWindow(local_folder_view_model, ignored_terms_view_model)
    window.show()

    try:
        return app.exec()
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
