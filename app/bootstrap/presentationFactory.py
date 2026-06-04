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
        self.controller.initialize()
        self.window.show()

        try:
            self.window.mainloop()
            return 0
        finally:
            self.controller.shutdown()
            self.serviceRegistry.session.close()


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
