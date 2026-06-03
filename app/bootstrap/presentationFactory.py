from __future__ import annotations

from dataclasses import dataclass

from app.bootstrap.serviceRegistry import ServiceRegistry
from app.presentation.styles import BASE_THEME, configureRootWindow
from app.presentation.windows.appShell import AppShellController
from app.presentation.windows.mainWindow import MainWindow


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


class PresentationFactory:
    def createDesktopApplication(
        self,
        app_name: str,
        service_registry: ServiceRegistry,
    ) -> DesktopApplication:
        window = MainWindow()
        configureRootWindow(window.window, app_name, theme=BASE_THEME)
        controller = AppShellController(
            window,
            local_folder_view_model=service_registry.localFolderViewModel,
            local_library_scan_view_model=service_registry.localLibraryScanViewModel,
            youtube_playlist_view_model=service_registry.youtubePlaylistViewModel,
            ignored_terms_view_model=service_registry.ignoredTermsViewModel,
        )
        return DesktopApplication(
            window=window,
            controller=controller,
            serviceRegistry=service_registry,
        )
