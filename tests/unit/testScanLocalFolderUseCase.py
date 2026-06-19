from __future__ import annotations

from app.application.dto.scanLocalFolderProgressDto import ScanLocalFolderProgressDto
from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.use_cases.library.scanLocalFolderUseCase import ScanLocalFolderUseCase
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong
from app.domain.metadata.services import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
)


class LocalFolderRepositorySpy:
    def __init__(self, active_folder: LocalFolder | None) -> None:
        self.active_folder = active_folder

    def get_active(self) -> LocalFolder | None:
        return self.active_folder


class LocalSongRepositorySpy:
    def __init__(self, existing_paths: set[str] | None = None) -> None:
        self.existing_paths = existing_paths or set()
        self.saved_songs: list[LocalSong] = []
        self.persisted_songs_by_id = {
            index: LocalSong(id=index, file_path=file_path, file_name="known.mp3")
            for index, file_path in enumerate(self.existing_paths, start=1)
        }

    def list_by_folder(self, _local_folder_id: int) -> list[LocalSong]:
        return list(self.persisted_songs_by_id.values())

    def get_by_file_path(self, file_path: str) -> LocalSong | None:
        for local_song in self.persisted_songs_by_id.values():
            if local_song.file_path == file_path:
                return local_song
        return None

    def save(self, local_song: LocalSong) -> LocalSong:
        self.saved_songs.append(local_song)
        self.existing_paths.add(local_song.file_path)
        persistedSong = local_song

        if local_song.id is None:
            nextId = len(self.persisted_songs_by_id) + 1
            persistedSong = LocalSong(
                id=nextId,
                local_folder_id=local_song.local_folder_id,
                download_id=local_song.download_id,
                file_path=local_song.file_path,
                file_name=local_song.file_name,
                is_available=local_song.is_available,
                title=local_song.title,
                artist=local_song.artist,
                normalized_title=local_song.normalized_title,
                normalized_artist=local_song.normalized_artist,
                album=local_song.album,
                release_year=local_song.release_year,
                track_number_album=local_song.track_number_album,
                duration_seconds=local_song.duration_seconds,
            )

        self.persisted_songs_by_id[persistedSong.id or 0] = persistedSong
        return persistedSong


class LocalMusicScannerSpy:
    def __init__(self, file_paths: list[str], error: Exception | None = None) -> None:
        self.file_paths = file_paths
        self.error = error
        self.received_folder_path: str | None = None

    def scanMp3Files(self, folderPath: str) -> list[str]:
        self.received_folder_path = folderPath
        if self.error is not None:
            raise self.error
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
    assert result.updated_song_count == 0
    assert result.existing_song_count == 1
    assert result.missing_song_count == 0
    assert result.moved_song_count == 0
    assert len(song_repository.saved_songs) == 2
    assert metadata_reader.received_file_paths == [
        r"C:\Music\Jazz\known.mp3",
        r"C:\Music\Jazz\new.mp3",
    ]
    assert song_repository.saved_songs[1].file_path == r"C:\Music\Jazz\new.mp3"
    assert song_repository.saved_songs[1].file_name == "new.mp3"
    assert song_repository.saved_songs[1].title == "New Song"
    assert song_repository.saved_songs[1].artist == "Miles Davis"
    assert song_repository.saved_songs[1].normalized_title == "new song"
    assert song_repository.saved_songs[1].normalized_artist == "miles davis"
    assert song_repository.saved_songs[1].album == "Kind of Blue"
    assert song_repository.saved_songs[1].release_year == 1959
    assert song_repository.saved_songs[1].track_number_album == 1
    assert song_repository.saved_songs[1].duration_seconds == 320.5


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


def test_execute_fails_with_clear_message_when_active_folder_does_not_exist() -> None:
    use_case = ScanLocalFolderUseCase(
        LocalFolderRepositorySpy(
            LocalFolder(
                id=7,
                path=r"C:\Music\Missing",
                display_name="Jazz",
                is_active=True,
            )
        ),
        LocalSongRepositorySpy(),
        LocalMusicScannerSpy([], error=FileNotFoundError(r"C:\Music\Missing")),
        LocalSongMetadataReaderSpy(),
    )

    try:
        use_case.execute()
    except ValueError as error:
        assert (
            str(error)
            == 'La carpeta local "Jazz" no existe o ya no esta disponible: C:\\Music\\Missing.'
        )
    else:
        raise AssertionError("Se esperaba ValueError cuando la carpeta activa no existe.")


def test_execute_fails_with_clear_message_when_active_folder_cannot_be_read() -> None:
    use_case = ScanLocalFolderUseCase(
        LocalFolderRepositorySpy(
            LocalFolder(
                id=7,
                path=r"C:\Music\Restricted",
                display_name="Jazz",
                is_active=True,
            )
        ),
        LocalSongRepositorySpy(),
        LocalMusicScannerSpy([], error=PermissionError(r"C:\Music\Restricted")),
        LocalSongMetadataReaderSpy(),
    )

    try:
        use_case.execute()
    except ValueError as error:
        assert (
            str(error)
            == 'No se puede leer la carpeta local "Jazz": C:\\Music\\Restricted. Revisa los permisos e intentalo de nuevo.'
        )
    else:
        raise AssertionError("Se esperaba ValueError cuando la carpeta activa no puede leerse.")


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
    assert result.updated_song_count == 0
    assert result.existing_song_count == 0
    assert result.missing_song_count == 0
    assert result.moved_song_count == 0


def test_execute_updates_metadata_for_existing_songs_without_creating_duplicates() -> None:
    existingPath = r"C:\Music\Jazz\known.mp3"
    song_repository = LocalSongRepositorySpy(existing_paths={existingPath})
    metadata_reader = LocalSongMetadataReaderSpy(
        {
            existingPath: LocalSongMetadataDto(
                title="Known Song",
                artist="John Coltrane",
                album="Blue Train",
                release_year=1957,
                track_number_album=1,
                duration_seconds=610.2,
            )
        }
    )
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
    assert result.updated_song_count == 1
    assert result.existing_song_count == 0
    assert result.missing_song_count == 0
    assert result.moved_song_count == 0
    assert metadata_reader.received_file_paths == [existingPath]
    assert len(song_repository.saved_songs) == 1
    assert song_repository.saved_songs[0].id == 1
    assert song_repository.saved_songs[0].title == "Known Song"
    assert song_repository.saved_songs[0].artist == "John Coltrane"
    assert song_repository.saved_songs[0].normalized_title == "known song"
    assert song_repository.saved_songs[0].normalized_artist == "john coltrane"
    assert song_repository.saved_songs[0].album == "Blue Train"
    assert song_repository.saved_songs[0].release_year == 1957
    assert song_repository.saved_songs[0].track_number_album == 1
    assert song_repository.saved_songs[0].duration_seconds == 610.2


def test_execute_marks_missing_songs_when_they_disappear_from_disk() -> None:
    missingPath = r"C:\Music\Jazz\missing.mp3"
    presentPath = r"C:\Music\Jazz\present.mp3"
    song_repository = LocalSongRepositorySpy(existing_paths={missingPath, presentPath})
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
        LocalMusicScannerSpy([presentPath]),
        LocalSongMetadataReaderSpy(
            {
                presentPath: LocalSongMetadataDto(
                    title="Present Song",
                    artist="Bill Evans",
                    album="Portrait in Jazz",
                    release_year=1960,
                    track_number_album=2,
                    duration_seconds=315.0,
                )
            }
        ),
    )

    result = use_case.execute()
    missingSong = next(song for song in song_repository.saved_songs if song.file_path == missingPath)

    assert result.scanned_file_count == 1
    assert result.created_song_count == 0
    assert result.updated_song_count == 1
    assert result.existing_song_count == 0
    assert result.missing_song_count == 1
    assert result.moved_song_count == 0
    assert missingSong.is_available is False


def test_execute_reconciles_moved_song_without_creating_duplicate() -> None:
    oldPath = r"C:\Music\Jazz\Old Folder\moved.mp3"
    newPath = r"C:\Music\Jazz\New Folder\moved.mp3"
    song_repository = LocalSongRepositorySpy(existing_paths={oldPath})
    originalSong = song_repository.get_by_file_path(oldPath)
    if originalSong is None:
        raise AssertionError("Se esperaba una cancion local persistida para la prueba.")
    song_repository.persisted_songs_by_id[originalSong.id or 0] = LocalSong(
        id=originalSong.id,
        local_folder_id=7,
        file_path=oldPath,
        file_name="moved.mp3",
        is_available=True,
        title="So What",
        artist="Miles Davis",
        normalized_title=normalizeMusicComparisonTitle("So What"),
        normalized_artist=normalizeMusicComparisonArtist("Miles Davis"),
        album="Kind of Blue",
        release_year=1959,
        track_number_album=1,
        duration_seconds=545.2,
    )
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
        LocalMusicScannerSpy([newPath]),
        LocalSongMetadataReaderSpy(
            {
                newPath: LocalSongMetadataDto(
                    title="So What",
                    artist="Miles Davis",
                    album="Kind of Blue",
                    release_year=1959,
                    track_number_album=1,
                    duration_seconds=545.2,
                )
            }
        ),
    )

    result = use_case.execute()
    persistedSongs = song_repository.list_by_folder(7)

    assert result.scanned_file_count == 1
    assert result.created_song_count == 0
    assert result.updated_song_count == 1
    assert result.existing_song_count == 0
    assert result.missing_song_count == 0
    assert result.moved_song_count == 1
    assert len(persistedSongs) == 1
    assert persistedSongs[0].id == originalSong.id
    assert persistedSongs[0].file_path == newPath
    assert persistedSongs[0].is_available is True


def test_execute_emits_progress_for_each_processed_song() -> None:
    progressEvents: list[ScanLocalFolderProgressDto] = []
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
        LocalMusicScannerSpy(
            [
                r"C:\Music\Jazz\first.mp3",
                r"C:\Music\Jazz\second.mp3",
            ]
        ),
        LocalSongMetadataReaderSpy(),
    )

    use_case.execute(on_progress=progressEvents.append)

    assert progressEvents == [
        ScanLocalFolderProgressDto(processed_song_count=0, total_song_count=2),
        ScanLocalFolderProgressDto(processed_song_count=1, total_song_count=2),
        ScanLocalFolderProgressDto(processed_song_count=2, total_song_count=2),
    ]


def test_execute_counts_existing_song_without_changes_as_not_updated() -> None:
    existingPath = r"C:\Music\Jazz\known.mp3"
    song_repository = LocalSongRepositorySpy(existing_paths={existingPath})
    originalSong = song_repository.get_by_file_path(existingPath)
    if originalSong is None:
        raise AssertionError("Se esperaba una cancion local persistida para la prueba.")
    song_repository.persisted_songs_by_id[originalSong.id or 0] = LocalSong(
        id=originalSong.id,
        local_folder_id=7,
        file_path=existingPath,
        file_name="known.mp3",
        is_available=True,
        title="Known Song",
        artist="John Coltrane",
        normalized_title=normalizeMusicComparisonTitle("Known Song"),
        normalized_artist=normalizeMusicComparisonArtist("John Coltrane"),
        album="Blue Train",
        release_year=1957,
        track_number_album=1,
        duration_seconds=610.2,
    )
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
        LocalSongMetadataReaderSpy(
            {
                existingPath: LocalSongMetadataDto(
                    title="Known Song",
                    artist="John Coltrane",
                    album="Blue Train",
                    release_year=1957,
                    track_number_album=1,
                    duration_seconds=610.2,
                )
            }
        ),
    )

    result = use_case.execute()

    assert result.created_song_count == 0
    assert result.updated_song_count == 0
    assert result.existing_song_count == 1
