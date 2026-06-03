from __future__ import annotations

from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.use_cases.library.scanLocalFolderUseCase import ScanLocalFolderUseCase
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong


class LocalFolderRepositorySpy:
    def __init__(self, active_folder: LocalFolder | None) -> None:
        self.active_folder = active_folder

    def get_active(self) -> LocalFolder | None:
        return self.active_folder


class LocalSongRepositorySpy:
    def __init__(self, existing_paths: set[str] | None = None) -> None:
        self.existing_paths = existing_paths or set()
        self.saved_songs: list[LocalSong] = []

    def list_by_folder(self, _local_folder_id: int) -> list[LocalSong]:
        return []

    def get_by_file_path(self, file_path: str) -> LocalSong | None:
        if file_path in self.existing_paths:
            return LocalSong(id=1, file_path=file_path, file_name="known.mp3")
        return None

    def save(self, local_song: LocalSong) -> LocalSong:
        self.saved_songs.append(local_song)
        self.existing_paths.add(local_song.file_path)
        return local_song


class LocalMusicScannerSpy:
    def __init__(self, file_paths: list[str]) -> None:
        self.file_paths = file_paths
        self.received_folder_path: str | None = None

    def scanMp3Files(self, folderPath: str) -> list[str]:
        self.received_folder_path = folderPath
        return list(self.file_paths)


class LocalSongMetadataReaderSpy:
    def __init__(self, metadata_by_path: dict[str, LocalSongMetadataDto] | None = None) -> None:
        self.metadata_by_path = metadata_by_path or {}
        self.received_file_paths: list[str] = []

    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        self.received_file_paths.append(filePath)
        return self.metadata_by_path.get(
            filePath,
            LocalSongMetadataDto("", "", "", 0, 0, 0.0),
        )


def test_execute_creates_only_new_local_songs_and_returns_summary() -> None:
    folder_repository = LocalFolderRepositorySpy(
        LocalFolder(
            id=7,
            path=r"C:\Music\Jazz",
            display_name="Jazz",
            is_active=True,
        )
    )
    song_repository = LocalSongRepositorySpy(existing_paths={r"C:\Music\Jazz\known.mp3"})
    scanner = LocalMusicScannerSpy(
        [
            r"C:\Music\Jazz\known.mp3",
            r"C:\Music\Jazz\new.mp3",
        ]
    )
    metadata_reader = LocalSongMetadataReaderSpy(
        {
            r"C:\Music\Jazz\new.mp3": LocalSongMetadataDto(
                title="New Song",
                artist="Miles Davis",
                album="Kind of Blue",
                release_year=1959,
                track_number_album=1,
                duration_seconds=320.5,
            )
        }
    )
    use_case = ScanLocalFolderUseCase(
        folder_repository,
        song_repository,
        scanner,
        metadata_reader,
    )

    result = use_case.execute()

    assert scanner.received_folder_path == r"C:\Music\Jazz"
    assert result.local_folder_id == 7
    assert result.local_folder_name == "Jazz"
    assert result.scanned_file_count == 2
    assert result.created_song_count == 1
    assert result.existing_song_count == 1
    assert len(song_repository.saved_songs) == 1
    assert metadata_reader.received_file_paths == [r"C:\Music\Jazz\new.mp3"]
    assert song_repository.saved_songs[0].file_path == r"C:\Music\Jazz\new.mp3"
    assert song_repository.saved_songs[0].file_name == "new.mp3"
    assert song_repository.saved_songs[0].title == "New Song"
    assert song_repository.saved_songs[0].artist == "Miles Davis"
    assert song_repository.saved_songs[0].album == "Kind of Blue"
    assert song_repository.saved_songs[0].release_year == 1959
    assert song_repository.saved_songs[0].track_number_album == 1
    assert song_repository.saved_songs[0].duration_seconds == 320.5


def test_execute_fails_when_there_is_no_active_local_folder() -> None:
    use_case = ScanLocalFolderUseCase(
        LocalFolderRepositorySpy(None),
        LocalSongRepositorySpy(),
        LocalMusicScannerSpy([]),
        LocalSongMetadataReaderSpy(),
    )

    try:
        use_case.execute()
    except ValueError as error:
        assert str(error) == "No hay una biblioteca local activa para escanear."
    else:
        raise AssertionError("Se esperaba ValueError cuando no hay biblioteca activa.")


def test_execute_returns_zero_counts_when_folder_has_no_mp3_files() -> None:
    use_case = ScanLocalFolderUseCase(
        LocalFolderRepositorySpy(
            LocalFolder(
                id=7,
                path=r"C:\Music\Jazz",
                display_name="Jazz",
                is_active=True,
            )
        ),
        LocalSongRepositorySpy(),
        LocalMusicScannerSpy([]),
        LocalSongMetadataReaderSpy(),
    )

    result = use_case.execute()

    assert result.scanned_file_count == 0
    assert result.created_song_count == 0
    assert result.existing_song_count == 0


def test_execute_does_not_duplicate_songs_on_rescan_when_all_mp3_are_already_registered() -> None:
    existingPath = r"C:\Music\Jazz\known.mp3"
    song_repository = LocalSongRepositorySpy(existing_paths={existingPath})
    metadata_reader = LocalSongMetadataReaderSpy()
    use_case = ScanLocalFolderUseCase(
        LocalFolderRepositorySpy(
            LocalFolder(
                id=7,
                path=r"C:\Music\Jazz",
                display_name="Jazz",
                is_active=True,
            )
        ),
        song_repository,
        LocalMusicScannerSpy([existingPath]),
        metadata_reader,
    )

    result = use_case.execute()

    assert result.scanned_file_count == 1
    assert result.created_song_count == 0
    assert result.existing_song_count == 1
    assert song_repository.saved_songs == []
    assert metadata_reader.received_file_paths == []
