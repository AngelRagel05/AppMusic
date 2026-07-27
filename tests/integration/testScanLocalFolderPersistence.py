from __future__ import annotations

from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.use_cases.library.scanLocalFolderUseCase import ScanLocalFolderUseCase
from app.infrastructure.persistence import (
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
)
from app.infrastructure.persistence.database.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class LocalMusicScannerSpy:
    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths = file_paths

    def scanMp3Files(self, folderPath: str) -> list[str]:
        return list(self.file_paths)


class LocalSongMetadataReaderSpy:
    def __init__(self, metadata_by_path: dict[str, LocalSongMetadataDto]) -> None:
        self.metadata_by_path = metadata_by_path

    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        return self.metadata_by_path[filePath]


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def create_active_folder(session: Session):
    repository = LocalFolderSqlAlchemyRepository(session)
    return repository.save_as_active(r"C:\Music\Jazz", "Jazz")


def test_scanLocalFolderUseCase_persists_multiple_mp3_into_sqlite_memory() -> None:
    session = create_session()
    create_active_folder(session)
    scanner = LocalMusicScannerSpy(
        [
            r"C:\Music\Jazz\first.mp3",
            r"C:\Music\Jazz\second.mp3",
        ]
    )
    metadata_reader = LocalSongMetadataReaderSpy(
        {
            r"C:\Music\Jazz\first.mp3": LocalSongMetadataDto(
                "First",
                "Artist A",
                "Album A",
                2020,
                1,
                180.0,
            ),
            r"C:\Music\Jazz\second.mp3": LocalSongMetadataDto(
                "Second",
                "Artist B",
                "Album B",
                2021,
                2,
                200.0,
            ),
        }
    )
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    use_case = ScanLocalFolderUseCase(
        LocalFolderSqlAlchemyRepository(session),
        local_song_repository,
        scanner,
        metadata_reader,
    )

    result = use_case.execute()
    persistedSongs = local_song_repository.list_by_folder(1)

    assert result.scanned_file_count == 2
    assert result.created_song_count == 2
    assert result.updated_song_count == 0
    assert result.existing_song_count == 0
    assert result.missing_song_count == 0
    assert result.moved_song_count == 0
    assert len(persistedSongs) == 2
    assert {song.title for song in persistedSongs} == {"First", "Second"}


def test_scanLocalFolderUseCase_rescan_does_not_duplicate_rows_in_sqlite_memory() -> None:
    session = create_session()
    create_active_folder(session)
    scanner = LocalMusicScannerSpy(
        [
            r"C:\Music\Jazz\first.mp3",
            r"C:\Music\Jazz\second.mp3",
        ]
    )
    metadata_reader = LocalSongMetadataReaderSpy(
        {
            r"C:\Music\Jazz\first.mp3": LocalSongMetadataDto(
                "First",
                "Artist A",
                "Album A",
                2020,
                1,
                180.0,
            ),
            r"C:\Music\Jazz\second.mp3": LocalSongMetadataDto(
                "Second",
                "Artist B",
                "Album B",
                2021,
                2,
                200.0,
            ),
        }
    )
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        scanner,
        metadata_reader,
    )

    firstResult = use_case.execute()
    secondResult = use_case.execute()
    persistedSongs = local_song_repository.list_by_folder(1)

    assert firstResult.created_song_count == 2
    assert secondResult.scanned_file_count == 2
    assert secondResult.created_song_count == 0
    assert secondResult.updated_song_count == 0
    assert secondResult.existing_song_count == 2
    assert secondResult.missing_song_count == 0
    assert secondResult.moved_song_count == 0
    assert len(persistedSongs) == 2


def test_scanLocalFolderUseCase_rescan_refreshes_metadata_for_existing_rows() -> None:
    session = create_session()
    create_active_folder(session)
    scanner = LocalMusicScannerSpy([r"C:\Music\Jazz\first.mp3"])
    first_metadata_reader = LocalSongMetadataReaderSpy(
        {
            r"C:\Music\Jazz\first.mp3": LocalSongMetadataDto(
                "First",
                "Artist A",
                "Album A",
                2020,
                1,
                180.0,
            )
        }
    )
    second_metadata_reader = LocalSongMetadataReaderSpy(
        {
            r"C:\Music\Jazz\first.mp3": LocalSongMetadataDto(
                "First Remastered",
                "Artist A",
                "Album A Deluxe",
                2024,
                7,
                182.5,
            )
        }
    )
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    first_use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        scanner,
        first_metadata_reader,
    )
    second_use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        scanner,
        second_metadata_reader,
    )

    first_use_case.execute()
    secondResult = second_use_case.execute()
    persistedSongs = local_song_repository.list_by_folder(1)

    assert secondResult.scanned_file_count == 1
    assert secondResult.created_song_count == 0
    assert secondResult.updated_song_count == 1
    assert secondResult.existing_song_count == 0
    assert secondResult.missing_song_count == 0
    assert secondResult.moved_song_count == 0
    assert len(persistedSongs) == 1
    assert persistedSongs[0].title == "First Remastered"
    assert persistedSongs[0].album == "Album A Deluxe"
    assert persistedSongs[0].release_year == 2024
    assert persistedSongs[0].track_number_album == 7
    assert persistedSongs[0].duration_seconds == 182.5


def test_scanLocalFolderUseCase_marks_missing_rows_when_a_file_disappears() -> None:
    session = create_session()
    create_active_folder(session)
    firstScanner = LocalMusicScannerSpy(
        [
            r"C:\Music\Jazz\first.mp3",
            r"C:\Music\Jazz\second.mp3",
        ]
    )
    secondScanner = LocalMusicScannerSpy([r"C:\Music\Jazz\first.mp3"])
    metadata_reader = LocalSongMetadataReaderSpy(
        {
            r"C:\Music\Jazz\first.mp3": LocalSongMetadataDto(
                "First",
                "Artist A",
                "Album A",
                2020,
                1,
                180.0,
            ),
            r"C:\Music\Jazz\second.mp3": LocalSongMetadataDto(
                "Second",
                "Artist B",
                "Album B",
                2021,
                2,
                200.0,
            ),
        }
    )
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    first_use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        firstScanner,
        metadata_reader,
    )
    second_use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        secondScanner,
        metadata_reader,
    )

    first_use_case.execute()
    secondResult = second_use_case.execute()
    persistedSongs = local_song_repository.list_by_folder(1)
    missingSong = next(song for song in persistedSongs if song.file_path.endswith("second.mp3"))

    assert secondResult.created_song_count == 0
    assert secondResult.updated_song_count == 0
    assert secondResult.existing_song_count == 1
    assert secondResult.missing_song_count == 1
    assert secondResult.moved_song_count == 0
    assert missingSong.is_available is False


def test_scanLocalFolderUseCase_reconciles_moved_song_by_updating_its_path() -> None:
    session = create_session()
    create_active_folder(session)
    firstPath = r"C:\Music\Jazz\Folder A\moved.mp3"
    movedPath = r"C:\Music\Jazz\Folder B\moved.mp3"
    firstScanner = LocalMusicScannerSpy([firstPath])
    secondScanner = LocalMusicScannerSpy([movedPath])
    first_metadata_reader = LocalSongMetadataReaderSpy(
        {
            firstPath: LocalSongMetadataDto(
                "So What",
                "Miles Davis",
                "Kind of Blue",
                1959,
                1,
                545.2,
            )
        }
    )
    second_metadata_reader = LocalSongMetadataReaderSpy(
        {
            movedPath: LocalSongMetadataDto(
                "So What",
                "Miles Davis",
                "Kind of Blue",
                1959,
                1,
                545.2,
            )
        }
    )
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    first_use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        firstScanner,
        first_metadata_reader,
    )
    second_use_case = ScanLocalFolderUseCase(
        local_folder_repository,
        local_song_repository,
        secondScanner,
        second_metadata_reader,
    )

    first_use_case.execute()
    secondResult = second_use_case.execute()
    persistedSongs = local_song_repository.list_by_folder(1)

    assert secondResult.created_song_count == 0
    assert secondResult.updated_song_count == 1
    assert secondResult.existing_song_count == 0
    assert secondResult.missing_song_count == 0
    assert secondResult.moved_song_count == 1
    assert len(persistedSongs) == 1
    assert persistedSongs[0].file_path == movedPath
    assert persistedSongs[0].is_available is True
