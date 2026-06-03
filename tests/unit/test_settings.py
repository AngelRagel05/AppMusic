from __future__ import annotations

from app.config.settings import get_settings


def test_settings_load_default_app_name() -> None:
    settings = get_settings()

    assert settings.app_name == "Music App"
