from __future__ import annotations

from dataclasses import dataclass

from app.bootstrap.serviceRegistry import ServiceRegistry
from app.infrastructure.filesystem import LocalFolderSnapshotReader
from app.presentation.styles import BASE_THEME, configureRootWindow
from app.presentation.windows.appShell import AppShellController
from app.presentation.windows.mainWindow import MainWindow
from app.workers import LocalFolderMonitorWorker


@dataclass
class DesktopApplication:
    window: MainWindow
    controller: AppShellController
    serviceRegistry: ServiceRegistry

    def run(self) -> int:
        self.window.show()
        self.window.page.showShellLoading(
            "Preparando vistas, estado local y configuracion activa..."
        )
        self.window.window.update_idletasks()
        self.window.window.after(0, self._initialize_bindings)

        try:
            self.window.mainloop()
            return 0
        finally:
            self.controller.shutdown()
            self.serviceRegistry.session.close()

    def _initialize_bindings(self) -> None:
        self.controller.initializeBindings()
        self.window.window.after(20, self._initialize_local_library)

    def _initialize_local_library(self) -> None:
        self.controller.initializeLocalLibrary()
        self.window.window.after(20, self._initialize_youtube_playlists)

    def _initialize_youtube_playlists(self) -> None:
        self.controller.initializeYoutubePlaylists()
        self.window.window.after(20, self._initialize_ignored_terms)

    def _initialize_ignored_terms(self) -> None:
        try:
            self.controller.initializeIgnoredTerms()
            self.controller.finalizeInitialization()
        finally:
            self.window.page.hideShellLoading()


class PresentationFactory:
    def createDesktopApplication(
        self,
        app_name: str,
        service_registry: ServiceRegistry,
    ) -> DesktopApplication:
        window = MainWindow()
        configureRootWindow(window.window, app_name, theme=BASE_THEME)
        localFolderMonitorWorker = LocalFolderMonitorWorker(
            snapshot_reader=LocalFolderSnapshotReader(),
            schedule_on_main_thread=lambda callback: window.window.after(0, callback),
            polling_interval_seconds=2.0,
        )
        controller = AppShellController(
            window,
            library_comparison_view_model=service_registry.libraryComparisonViewModel,
            local_folder_view_model=service_registry.localFolderViewModel,
            local_library_scan_view_model=service_registry.localLibraryScanViewModel,
            local_folder_monitor_worker=localFolderMonitorWorker,
            youtube_playlist_import_view_model=service_registry.youtubePlaylistImportViewModel,
            youtube_playlist_view_model=service_registry.youtubePlaylistViewModel,
            ignored_terms_view_model=service_registry.ignoredTermsViewModel,
        )
        return DesktopApplication(
            window=window,
            controller=controller,
            serviceRegistry=service_registry,
        )
