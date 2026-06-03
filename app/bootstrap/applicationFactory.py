from __future__ import annotations

from dataclasses import dataclass

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
    ListIgnoredTermsUseCase,
    ListLocalFoldersUseCase,
    ListYoutubePlaylistsUseCase,
    UpdateIgnoredTermUseCase,
    UpdateLocalFolderUseCase,
    UpdateYoutubePlaylistUseCase,
)
from app.bootstrap.serviceRegistry import ServiceRegistry
from app.infrastructure.database import DatabaseBootstrapper, SessionLocal, engine, get_session
from app.infrastructure.repositories import (
    IgnoredTermSqlAlchemyRepository,
    LocalFolderSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.presentation.features.ignoredTerms.viewmodel import IgnoredTermsViewModel
from app.presentation.features.localLibrary.viewmodel import LocalFolderViewModel
from app.presentation.features.youtubePlaylists.viewmodel import YoutubePlaylistViewModel
from app.presentation.shell.appShell import AppShellController
from app.presentation.shell.mainWindow import MainWindow
from app.presentation.shared.theme import BASE_THEME, configureRootWindow


@dataclass
class DesktopApplication:
    window: MainWindow
    controller: AppShellController
    serviceRegistry: ServiceRegistry

    def run(self) -> int:
        self.controller.initialize()
        self.window.show()

        try:
            self.window.mainloop()
            return 0
        finally:
            self.serviceRegistry.session.close()


class ApplicationFactory:
    def bootstrapDatabase(self) -> None:
        BootstrapDatabaseUseCase(DatabaseBootstrapper(engine, SessionLocal)).execute()

    def createServiceRegistry(self) -> ServiceRegistry:
        session = get_session()

        ignoredTermRepository = IgnoredTermSqlAlchemyRepository(session)
        localFolderRepository = LocalFolderSqlAlchemyRepository(session)
        youtubePlaylistRepository = YoutubePlaylistSqlAlchemyRepository(session)

        ignoredTermsViewModel = IgnoredTermsViewModel(
            list_use_case=ListIgnoredTermsUseCase(ignoredTermRepository),
            create_use_case=CreateIgnoredTermUseCase(ignoredTermRepository),
            update_use_case=UpdateIgnoredTermUseCase(ignoredTermRepository),
            delete_use_case=DeleteIgnoredTermUseCase(ignoredTermRepository),
        )
        localFolderViewModel = LocalFolderViewModel(
            list_use_case=ListLocalFoldersUseCase(localFolderRepository),
            get_active_use_case=GetActiveLocalFolderUseCase(localFolderRepository),
            activate_use_case=ActivateLocalFolderUseCase(localFolderRepository),
            define_main_use_case=DefineMainLocalFolderUseCase(localFolderRepository),
            update_use_case=UpdateLocalFolderUseCase(localFolderRepository),
            delete_use_case=DeleteLocalFolderUseCase(localFolderRepository),
        )
        youtubePlaylistViewModel = YoutubePlaylistViewModel(
            list_use_case=ListYoutubePlaylistsUseCase(youtubePlaylistRepository),
            get_active_use_case=GetActiveYoutubePlaylistUseCase(youtubePlaylistRepository),
            activate_use_case=ActivateYoutubePlaylistUseCase(youtubePlaylistRepository),
            define_main_use_case=DefineMainYoutubePlaylistUseCase(
                youtubePlaylistRepository
            ),
            update_use_case=UpdateYoutubePlaylistUseCase(youtubePlaylistRepository),
            delete_use_case=DeleteYoutubePlaylistUseCase(youtubePlaylistRepository),
        )

        return ServiceRegistry(
            session=session,
            ignoredTermsViewModel=ignoredTermsViewModel,
            localFolderViewModel=localFolderViewModel,
            youtubePlaylistViewModel=youtubePlaylistViewModel,
        )

    def createDesktopApplication(self, appName: str) -> DesktopApplication:
        serviceRegistry = self.createServiceRegistry()
        window = MainWindow()
        configureRootWindow(window.window, appName, theme=BASE_THEME)
        controller = AppShellController(
            window,
            local_folder_view_model=serviceRegistry.localFolderViewModel,
            youtube_playlist_view_model=serviceRegistry.youtubePlaylistViewModel,
            ignored_terms_view_model=serviceRegistry.ignoredTermsViewModel,
        )
        return DesktopApplication(
            window=window,
            controller=controller,
            serviceRegistry=serviceRegistry,
        )
