from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.application.use_cases import (
    ActivateLocalFolderUseCase,
    ActivateYoutubePlaylistUseCase,
    BootstrapDatabaseUseCase,
    CreateIgnoredTermUseCase,
    DefineMainLocalFolderUseCase,
    DefineMainYoutubePlaylistUseCase,
    GetActiveLocalFolderUseCase,
    GetActiveYoutubePlaylistUseCase,
    ListLocalFoldersUseCase,
    ListYoutubePlaylistsUseCase,
    ListIgnoredTermsUseCase,
)
from app.config.settings import get_settings
from app.infrastructure.database import DatabaseBootstrapper, SessionLocal, engine, get_session
from app.infrastructure.repositories import (
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.presentation.styles import loadQss
from app.presentation.ui.mainScreen.mainWindow.mainWindow import MainWindow
from app.presentation.controllers.mainWindowController import MainWindowController
from app.presentation.viewmodels import (
    IgnoredTermsViewModel,
    LocalFolderViewModel,
    YoutubePlaylistViewModel,
)
from app.utils.logging import configure_logging


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    BootstrapDatabaseUseCase(DatabaseBootstrapper(engine, SessionLocal)).execute()
    session = get_session()

    ignored_term_repository = IgnoredTermSqlAlchemyRepository(session)
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    youtube_playlist_repository = YoutubePlaylistSqlAlchemyRepository(session)
    ignored_terms_view_model = IgnoredTermsViewModel(
        list_use_case=ListIgnoredTermsUseCase(ignored_term_repository),
        create_use_case=CreateIgnoredTermUseCase(ignored_term_repository),
    )
    local_folder_view_model = LocalFolderViewModel(
        list_use_case=ListLocalFoldersUseCase(local_folder_repository),
        get_active_use_case=GetActiveLocalFolderUseCase(local_folder_repository),
        activate_use_case=ActivateLocalFolderUseCase(local_folder_repository),
        define_main_use_case=DefineMainLocalFolderUseCase(local_folder_repository),
    )
    youtube_playlist_view_model = YoutubePlaylistViewModel(
        list_use_case=ListYoutubePlaylistsUseCase(youtube_playlist_repository),
        get_active_use_case=GetActiveYoutubePlaylistUseCase(youtube_playlist_repository),
        activate_use_case=ActivateYoutubePlaylistUseCase(youtube_playlist_repository),
        define_main_use_case=DefineMainYoutubePlaylistUseCase(youtube_playlist_repository),
    )

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    app.setStyleSheet(loadQss("app/presentation/styles/global.qss"))

    window = MainWindow()
    controller = MainWindowController(
        window,
        local_folder_view_model=local_folder_view_model,
        youtube_playlist_view_model=youtube_playlist_view_model,
        ignored_terms_view_model=ignored_terms_view_model,
    )
    controller.initialize()
    window.show()

    try:
        return app.exec()
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
