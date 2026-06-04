from __future__ import annotations

from app.application.use_cases import ListActiveLocalSongsUseCase
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong


class LocalFolderRepositorySpy:
    def __init__(self, active_folder: LocalFolder | None) -> None:
        self.active_folder = active_folder

    def get_active(self) -> LocalFolder | None:
        return self.active_folder


class LocalSongRepositorySpy:
    def __init__(self, songs: list[LocalSong]) -> None:
        self.songs = songs
        self.list_by_folder_calls: list[int] = []

    def list_by_folder(self, local_folder_id: int) -> list[LocalSong]:
        self.list_by_folder_calls.append(local_folder_id)
        return list(self.songs)


def test_execute_returns_empty_when_no_active_local_folder_exists() -> None:
    use_case = ListActiveLocalSongsUseCase(
        local_folder_repository=LocalFolderRepositorySpy(None),
        local_song_repository=LocalSongRepositorySpy([]),
    )

    assert use_case.execute() == []


def test_execute_returns_only_available_songs_from_active_local_folder() -> None:
    use_case = ListActiveLocalSongsUseCase(
        local_folder_repository=LocalFolderRepositorySpy(
            LocalFolder(id=7, path=r"C:\Music\Active", display_name="Active", is_active=True)
        ),
        local_song_repository=LocalSongRepositorySpy(
            [
                LocalSong(
                    id=1,
                    local_folder_id=7,
                    file_path=r"C:\Music\Active\song-one.mp3",
                    file_name="song-one.mp3",
                    is_available=True,
                    title="Song One",
                    artist="Artist One",
                    album="Album One",
                    release_year=2024,
                    track_number_album=1,
                    duration_seconds=180.0,
                ),
                LocalSong(
                    id=2,
                    local_folder_id=7,
                    file_path=r"C:\Music\Active\missing.mp3",
                    file_name="missing.mp3",
                    is_available=False,
                    title="Missing",
                    artist="Artist Two",
                    album="Album Two",
                    release_year=2023,
                    track_number_album=2,
                    duration_seconds=200.0,
                ),
            ]
        ),
    )

    local_songs = use_case.execute()

    assert len(local_songs) == 1
    assert local_songs[0].title == "Song One"
    assert local_songs[0].file_name == "song-one.mp3"
