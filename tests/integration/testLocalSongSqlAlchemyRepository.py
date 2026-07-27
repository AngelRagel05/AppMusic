from __future__ import annotations

from app.domain.library.entities.localSong import LocalSong
from app.domain.metadata.services import (
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonTitle,
)
from app.infrastructure.persistence import (
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
)
from app.infrastructure.persistence.database.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def create_local_folder(session: Session):
    repository = LocalFolderSqlAlchemyRepository(session)
    return repository.save_as_active(r"C:\Music\Rap", "Rap")


def test_save_persists_local_song() -> None:
    session = create_session()
    folder = create_local_folder(session)
    repository = LocalSongSqlAlchemyRepository(session)

    local_song = repository.save(
        LocalSong(
            local_folder_id=folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            title="Song",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.5,
        )
    )

    assert local_song.id is not None
    assert local_song.file_name == "song.mp3"
    assert local_song.local_folder_id == folder.id
    assert local_song.is_available is True
    assert local_song.title == "Song"
    assert local_song.artist == "Artist"
    assert local_song.normalized_title == "song"
    assert local_song.normalized_artist == "artist"
    assert local_song.album == "Album"
    assert local_song.release_year == 2024
    assert local_song.track_number_album == 1
    assert local_song.duration_seconds == 180.5


def test_get_by_file_path_returns_saved_local_song() -> None:
    session = create_session()
    folder = create_local_folder(session)
    repository = LocalSongSqlAlchemyRepository(session)
    repository.save(
        LocalSong(
            local_folder_id=folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            title="Song",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.5,
        )
    )

    local_song = repository.get_by_file_path(r"C:\Music\Rap\song.mp3")

    assert local_song is not None
    assert local_song.is_available is True
    assert local_song.title == "Song"


def test_list_by_folder_returns_only_songs_for_selected_folder() -> None:
    session = create_session()
    folder_repository = LocalFolderSqlAlchemyRepository(session)
    first_folder = folder_repository.save_as_active(r"C:\Music\Rap", "Rap")
    second_folder = folder_repository.save_as_active(r"C:\Music\Rock", "Rock")
    repository = LocalSongSqlAlchemyRepository(session)

    repository.save(
        LocalSong(
            local_folder_id=first_folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            title="Song",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.5,
        )
    )
    repository.save(
        LocalSong(
            local_folder_id=second_folder.id,
            file_path=r"C:\Music\Rock\other.mp3",
            file_name="other.mp3",
            title="Other",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Other"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2023,
            track_number_album=2,
            duration_seconds=200.0,
        )
    )

    local_songs = repository.list_by_folder(first_folder.id or 0)

    assert len(local_songs) == 1
    assert local_songs[0].file_path == r"C:\Music\Rap\song.mp3"


def test_save_updates_existing_song_when_file_path_already_exists() -> None:
    session = create_session()
    folder = create_local_folder(session)
    repository = LocalSongSqlAlchemyRepository(session)

    first_song = repository.save(
        LocalSong(
            local_folder_id=folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            title="Song",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.5,
        )
    )

    updated_song = repository.save(
        LocalSong(
            local_folder_id=folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            title="Song remaster",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song remaster"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2025,
            track_number_album=3,
            duration_seconds=181.0,
        )
    )

    assert updated_song.id == first_song.id
    assert updated_song.is_available is True
    assert updated_song.title == "Song remaster"
    assert updated_song.normalized_title == "song remaster"
    assert updated_song.release_year == 2025


def test_save_updates_song_availability_state() -> None:
    session = create_session()
    folder = create_local_folder(session)
    repository = LocalSongSqlAlchemyRepository(session)

    first_song = repository.save(
        LocalSong(
            local_folder_id=folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            is_available=True,
            title="Song",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.5,
        )
    )

    updated_song = repository.save(
        LocalSong(
            id=first_song.id,
            local_folder_id=folder.id,
            file_path=r"C:\Music\Rap\song.mp3",
            file_name="song.mp3",
            is_available=False,
            title="Song",
            artist="Artist",
            normalized_title=normalizeMusicComparisonTitle("Song"),
            normalized_artist=normalizeMusicComparisonArtist("Artist"),
            album="Album",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.5,
        )
    )

    assert updated_song.id == first_song.id
    assert updated_song.is_available is False
