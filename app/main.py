from __future__ import annotations

import uvicorn

from app.api import createApi
from app.config.settings import get_settings
from app.shared.utils import configure_logging

app = createApi()


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
