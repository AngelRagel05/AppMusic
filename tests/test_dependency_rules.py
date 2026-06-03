from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"

FORBIDDEN_WIDGET_IMPORT_PREFIXES = (
    "sqlalchemy",
    "pygame",
    "yt_dlp",
    "mutagen",
    "ffmpeg",
)


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _module_name(path: Path) -> str:
    return ".".join(path.relative_to(PROJECT_ROOT).with_suffix("").parts)


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
            continue

        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            imported_modules.append(node.module)

    return imported_modules


def test_presentation_does_not_depend_on_infrastructure() -> None:
    violations: list[str] = []

    for path in _python_files(APP_ROOT / "presentation"):
        module_name = _module_name(path)
        for imported_module in _imported_modules(path):
            if imported_module.startswith("app.infrastructure"):
                violations.append(f"{module_name} -> {imported_module}")

    assert violations == []


def test_domain_does_not_depend_on_infrastructure() -> None:
    violations: list[str] = []

    for path in _python_files(APP_ROOT / "domain"):
        module_name = _module_name(path)
        for imported_module in _imported_modules(path):
            if imported_module.startswith("app.infrastructure"):
                violations.append(f"{module_name} -> {imported_module}")

    assert violations == []


def test_widgets_do_not_depend_on_external_integration_packages() -> None:
    violations: list[str] = []

    for path in _python_files(APP_ROOT / "presentation" / "widgets"):
        module_name = _module_name(path)
        for imported_module in _imported_modules(path):
            if imported_module.startswith(FORBIDDEN_WIDGET_IMPORT_PREFIXES):
                violations.append(f"{module_name} -> {imported_module}")

    assert violations == []
