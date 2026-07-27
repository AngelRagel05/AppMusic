from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

project_root = Path(SPEC).resolve().parent.parent
icon_path = project_root / "desktop" / "assets" / "soundShelfIcon.png"

datas = [
    (str(project_root / "alembic.ini"), "."),
    (str(project_root / "migrations"), "migrations"),
]
datas += collect_data_files("certifi")
datas += collect_data_files("yt_dlp")
datas += copy_metadata("yt-dlp")

hidden_imports = collect_submodules("app")
hidden_imports += collect_submodules("yt_dlp")
hidden_imports += collect_submodules("sqlalchemy.dialects.sqlite")
hidden_imports += [
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
]

analysis = Analysis(
    [str(project_root / "app" / "desktopMain.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="SoundShelfBackend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path),
)

bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SoundShelfBackend",
)
