from __future__ import annotations

import argparse

from loguru import logger

from music_app.app.application.use_cases.scan_music_folder import ScanMusicFolderUseCase
from music_app.app.config.settings import get_settings
from music_app.app.infrastructure.database.bootstrap import bootstrap_database
from music_app.app.infrastructure.database.session import get_session
from music_app.app.infrastructure.filesystem.music_scanner import MusicScanner
from music_app.app.infrastructure.metadata.reader import MetadataReader
from music_app.app.infrastructure.repositories.song_repository import SqlAlchemySongRepository
from music_app.app.utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan a music folder and persist MP3 songs.")
    parser.add_argument("--path", type=str, help="Path to the music folder to scan.")
    return parser


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    bootstrap_database()

    args = build_parser().parse_args()
    folder_path = args.path or settings.music_scan_path

    if not folder_path:
        raise SystemExit("Missing music path. Use --path or define MUSIC_SCAN_PATH in .env")

    session = get_session()
    try:
        use_case = ScanMusicFolderUseCase(
            song_repository=SqlAlchemySongRepository(session),
            music_scanner=MusicScanner(),
            metadata_reader=MetadataReader(),
        )
        result = use_case.execute(folder_path)
    finally:
        session.close()

    logger.info(
        "Scan complete. scanned_files={}, imported_songs={}, skipped_existing={}",
        result.scanned_files,
        result.imported_songs,
        result.skipped_existing,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

