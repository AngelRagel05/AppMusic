from __future__ import annotations

from app.application.use_cases import (
    ActivateLocalFolderUseCase,
    ActivateYoutubePlaylistUseCase,
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
from app.bootstrap.persistenceFactory import PersistenceFactory
from app.bootstrap.presentationFactory import DesktopApplication, PresentationFactory
from app.bootstrap.serviceRegistry import ServiceRegistry
from app.presentation.viewmodels import (
    IgnoredTermsViewModel,
    LocalFolderViewModel,
    YoutubePlaylistViewModel,
)


class ApplicationFactory:
    def __init__(
        self,
        persistence_factory: PersistenceFactory | None = None,
        presentation_factory: PresentationFactory | None = None,
    ) -> None:
        self._persistence_factory = persistence_factory or PersistenceFactory()
        self._presentation_factory = presentation_factory or PresentationFactory()

    def bootstrapDatabase(self) -> None:
        self._persistence_factory.bootstrapDatabase()

    def createServiceRegistry(self) -> ServiceRegistry:
        persistence_registry = self._persistence_factory.createRegistry()

        ignoredTermsViewModel = IgnoredTermsViewModel(
            list_use_case=ListIgnoredTermsUseCase(
                persistence_registry.ignoredTermRepository
            ),
            create_use_case=CreateIgnoredTermUseCase(
                persistence_registry.ignoredTermRepository
            ),
            update_use_case=UpdateIgnoredTermUseCase(
                persistence_registry.ignoredTermRepository
            ),
            delete_use_case=DeleteIgnoredTermUseCase(
                persistence_registry.ignoredTermRepository
            ),
        )
        localFolderViewModel = LocalFolderViewModel(
            list_use_case=ListLocalFoldersUseCase(
                persistence_registry.localFolderRepository
            ),
            get_active_use_case=GetActiveLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            activate_use_case=ActivateLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            define_main_use_case=DefineMainLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            update_use_case=UpdateLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
            delete_use_case=DeleteLocalFolderUseCase(
                persistence_registry.localFolderRepository
            ),
        )
        youtubePlaylistViewModel = YoutubePlaylistViewModel(
            list_use_case=ListYoutubePlaylistsUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            get_active_use_case=GetActiveYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            activate_use_case=ActivateYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            define_main_use_case=DefineMainYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            update_use_case=UpdateYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
            delete_use_case=DeleteYoutubePlaylistUseCase(
                persistence_registry.youtubePlaylistRepository
            ),
        )

        return ServiceRegistry(
            session=persistence_registry.session,
            ignoredTermsViewModel=ignoredTermsViewModel,
            localFolderViewModel=localFolderViewModel,
            youtubePlaylistViewModel=youtubePlaylistViewModel,
        )

    def createDesktopApplication(self, appName: str) -> DesktopApplication:
        service_registry = self.createServiceRegistry()
        return self._presentation_factory.createDesktopApplication(
            app_name=appName,
            service_registry=service_registry,
        )
