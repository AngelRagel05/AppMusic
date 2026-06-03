from __future__ import annotations

from app.application.use_cases import (
    ActivateLocalFolderUseCase,
    ActivateYoutubePlaylistUseCase,
    BootstrapDatabaseUseCase,
    CreateIgnoredTermUseCase,
    DeleteIgnoredTermUseCase,
    DeleteLocalFolderUseCase,
    DeleteYoutubePlaylistUseCase,
    DefineMainLocalFolderUseCase,
    DefineMainYoutubePlaylistUseCase,
    GetActiveLocalFolderUseCase,
    GetActiveYoutubePlaylistUseCase,
    ListLocalFoldersUseCase,
    ListYoutubePlaylistsUseCase,
    ListIgnoredTermsUseCase,
    UpdateLocalFolderUseCase,
    UpdateIgnoredTermUseCase,
    UpdateYoutubePlaylistUseCase,
)
from app.config.settings import get_settings
from app.infrastructure.database import DatabaseBootstrapper, SessionLocal, engine, get_session
from app.infrastructure.repositories import (
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.presentation.uiTheme import BASE_THEME, configureRootWindow
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
        update_use_case=UpdateIgnoredTermUseCase(ignored_term_repository),
        delete_use_case=DeleteIgnoredTermUseCase(ignored_term_repository),
    )
    local_folder_view_model = LocalFolderViewModel(
        list_use_case=ListLocalFoldersUseCase(local_folder_repository),
        get_active_use_case=GetActiveLocalFolderUseCase(local_folder_repository),
        activate_use_case=ActivateLocalFolderUseCase(local_folder_repository),
        define_main_use_case=DefineMainLocalFolderUseCase(local_folder_repository),
        update_use_case=UpdateLocalFolderUseCase(local_folder_repository),
        delete_use_case=DeleteLocalFolderUseCase(local_folder_repository),
    )
    youtube_playlist_view_model = YoutubePlaylistViewModel(
        list_use_case=ListYoutubePlaylistsUseCase(youtube_playlist_repository),
        get_active_use_case=GetActiveYoutubePlaylistUseCase(youtube_playlist_repository),
        activate_use_case=ActivateYoutubePlaylistUseCase(youtube_playlist_repository),
        define_main_use_case=DefineMainYoutubePlaylistUseCase(youtube_playlist_repository),
        update_use_case=UpdateYoutubePlaylistUseCase(youtube_playlist_repository),
        delete_use_case=DeleteYoutubePlaylistUseCase(youtube_playlist_repository),
    )

    window = MainWindow()
    configureRootWindow(window.window, settings.app_name, theme=BASE_THEME)
    controller = MainWindowController(
        window,
        local_folder_view_model=local_folder_view_model,
        youtube_playlist_view_model=youtube_playlist_view_model,
        ignored_terms_view_model=ignored_terms_view_model,
    )
    controller.initialize()
    window.show()

    try:
        window.mainloop()
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
