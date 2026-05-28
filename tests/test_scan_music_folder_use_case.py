from __future__ import annotations

from pathlib import Path

from music_app.app.application.use_cases.scan_music_folder import ScanMusicFolderUseCase
from music_app.app.domain.entities.song import Song
from music_app.app.domain.services.song_repository import SongRepository
from music_app.app.infrastructure.metadata.reader import MetadataReader, SongMetadata


class InMemorySongRepository(SongRepository):
    def __init__(self) -> None:
        self._songs: dict[str, Song] = {}
        self._next_id = 1

    def get_by_path(self, path: str) -> Song | None:
        return self._songs.get(path)

    def add(self, song: Song) -> Song:
        song.id = self._next_id
        self._next_id += 1
        self._songs[song.path] = song
        return song


class FakeMusicScanner:
    def __init__(self, files: list[Path]) -> None:
        self._files = files

    def scan(self, root_path: Path) -> list[Path]:
        return self._files


class FakeMetadataReader(MetadataReader):
    def read(self, file_path: Path) -> SongMetadata:
        return SongMetadata(
            title=file_path.stem,
            artist="Artist",
            album="Album",
            year=2024,
            track_number=1,
            duration=180.0,
        )


def test_scan_music_folder_imports_new_files(tmp_path: Path) -> None:
    first_song = tmp_path / "track01.mp3"
    second_song = tmp_path / "track02.mp3"
    first_song.write_bytes(b"fake")
    second_song.write_bytes(b"fake")

    use_case = ScanMusicFolderUseCase(
        song_repository=InMemorySongRepository(),
        music_scanner=FakeMusicScanner([first_song, second_song]),
        metadata_reader=FakeMetadataReader(),
    )

    result = use_case.execute(str(tmp_path))

    assert result.scanned_files == 2
    assert result.imported_songs == 2
    assert result.skipped_existing == 0
