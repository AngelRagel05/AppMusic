from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.database.base import Base
from app.infrastructure.database.models import YoutubePlaylist as YoutubePlaylistModel
from app.infrastructure.repositories import YoutubePlaylistSqlAlchemyRepository


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def test_get_active_returns_none_when_there_is_no_active_playlist() -> None:
    session = create_session()
    repository = YoutubePlaylistSqlAlchemyRepository(session)

    assert repository.get_active() is None


def test_list_all_returns_saved_playlists() -> None:
    session = create_session()
    repository = YoutubePlaylistSqlAlchemyRepository(session)

    repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLFIRST",
        "PLFIRST",
        "Playlist PLFIRST",
    )
    repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLSECOND",
        "PLSECOND",
        "Playlist PLSECOND",
    )

    youtube_playlists = repository.list_all()

    assert len(youtube_playlists) == 2


def test_save_as_active_persists_playlist_and_marks_it_active() -> None:
    session = create_session()
    repository = YoutubePlaylistSqlAlchemyRepository(session)

    youtube_playlist = repository.save_as_active(
        "https://www.youtube.com/playlist?list=PL123",
        "PL123",
        "Playlist PL123",
    )

    assert youtube_playlist.id is not None
    assert youtube_playlist.is_active is True
    assert session.query(YoutubePlaylistModel).count() == 1


def test_save_as_active_deactivates_previous_active_playlist() -> None:
    session = create_session()
    repository = YoutubePlaylistSqlAlchemyRepository(session)

    repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLFIRST",
        "PLFIRST",
        "Playlist PLFIRST",
    )
    repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLSECOND",
        "PLSECOND",
        "Playlist PLSECOND",
    )

    active_playlists = (
        session.query(YoutubePlaylistModel)
        .filter(YoutubePlaylistModel.is_active.is_(True))
        .all()
    )

    assert len(active_playlists) == 1
    assert active_playlists[0].external_playlist_id == "PLSECOND"


def test_activate_switches_back_to_an_existing_playlist() -> None:
    session = create_session()
    repository = YoutubePlaylistSqlAlchemyRepository(session)

    first_youtube_playlist = repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLFIRST",
        "PLFIRST",
        "Playlist PLFIRST",
    )
    repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLSECOND",
        "PLSECOND",
        "Playlist PLSECOND",
    )

    activated_playlist = repository.activate(first_youtube_playlist.id or 0)

    assert activated_playlist.id == first_youtube_playlist.id
    assert activated_playlist.is_active is True
    active_playlist = repository.get_active()
    assert active_playlist is not None
    assert active_playlist.id == first_youtube_playlist.id
