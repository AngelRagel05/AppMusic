from __future__ import annotations

from app.bootstrap import ApplicationFactory
from app.config.settings import get_settings
from app.shared.utils import configure_logging


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    applicationFactory = ApplicationFactory()
    applicationFactory.bootstrapDatabase()
    desktopApplication = applicationFactory.createDesktopApplication(settings.app_name)
    return desktopApplication.run()


if __name__ == "__main__":
    raise SystemExit(main())
