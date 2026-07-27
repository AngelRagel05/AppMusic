from __future__ import annotations

from datetime import UTC, datetime

from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.infrastructure.persistence import (
    YoutubePlaylistItemSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import (
    YoutubePlaylistItem as YoutubePlaylistItemModel,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def create_youtube_playlist(session: Session):
    repository = YoutubePlaylistSqlAlchemyRepository(session)
    return repository.save_as_active(
        "https://www.youtube.com/playlist?list=PL123",
        "PL123",
        "Favoritas",
    )


def test_replace_for_playlist_inserts_items() -> None:
    session = create_session()
    playlist = create_youtube_playlist(session)
    repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    persisted_items = repository.replace_for_playlist(
        playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="abc123",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
                published_at=datetime(2024, 6, 1, tzinfo=UTC),
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="def456",
                position=2,
                raw_title="Song Two",
                raw_channel_name="Artist Two",
                normalized_title="song two",
                normalized_artist="artist two",
            ),
        ],
    )

    assert len(persisted_items) == 2
    assert persisted_items[0].id is not None
    assert persisted_items[0].external_video_id == "abc123"
    assert persisted_items[0].youtube_playlist_id == playlist.id
    assert persisted_items[0].published_at == datetime(2024, 6, 1, tzinfo=UTC)


def test_replace_for_playlist_replaces_previous_snapshot() -> None:
    session = create_session()
    playlist = create_youtube_playlist(session)
    repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    repository.replace_for_playlist(
        playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="obsolete",
                position=1,
                raw_title="Obsolete Song",
                raw_channel_name="Obsolete Artist",
                normalized_title="obsolete song",
                normalized_artist="obsolete artist",
            )
        ],
    )

    persisted_items = repository.replace_for_playlist(
        playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="fresh",
                position=1,
                raw_title="Fresh Song",
                raw_channel_name="Fresh Artist",
                normalized_title="fresh song",
                normalized_artist="fresh artist",
            )
        ],
    )

    assert len(persisted_items) == 1
    assert persisted_items[0].external_video_id == "fresh"


def test_list_by_playlist_returns_items_ordered_by_position() -> None:
    session = create_session()
    playlist = create_youtube_playlist(session)
    repository = YoutubePlaylistItemSqlAlchemyRepository(session)
    repository.replace_for_playlist(
        playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="late",
                position=3,
                raw_title="Late Song",
                raw_channel_name="Artist Three",
                normalized_title="late song",
                normalized_artist="artist three",
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="first",
                position=1,
                raw_title="First Song",
                raw_channel_name="Artist One",
                normalized_title="first song",
                normalized_artist="artist one",
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="middle",
                position=2,
                raw_title="Middle Song",
                raw_channel_name="Artist Two",
                normalized_title="middle song",
                normalized_artist="artist two",
            ),
        ],
    )

    persisted_items = repository.list_by_playlist(playlist.id or 0)

    assert [item.position for item in persisted_items] == [1, 2, 3]
    assert [item.external_video_id for item in persisted_items] == ["first", "middle", "late"]


def test_list_by_playlist_returns_only_items_for_selected_playlist() -> None:
    session = create_session()
    playlist_repository = YoutubePlaylistSqlAlchemyRepository(session)
    first_playlist = playlist_repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLFIRST",
        "PLFIRST",
        "Primera",
    )
    second_playlist = playlist_repository.save_as_active(
        "https://www.youtube.com/playlist?list=PLSECOND",
        "PLSECOND",
        "Segunda",
    )
    repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    repository.replace_for_playlist(
        first_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=first_playlist.id or 0,
                external_video_id="first-item",
                position=1,
                raw_title="First Song",
                raw_channel_name="Artist One",
                normalized_title="first song",
                normalized_artist="artist one",
            )
        ],
    )
    repository.replace_for_playlist(
        second_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=second_playlist.id or 0,
                external_video_id="second-item",
                position=1,
                raw_title="Second Song",
                raw_channel_name="Artist Two",
                normalized_title="second song",
                normalized_artist="artist two",
            )
        ],
    )

    persisted_items = repository.list_by_playlist(first_playlist.id or 0)

    assert len(persisted_items) == 1
    assert persisted_items[0].youtube_playlist_id == first_playlist.id
    assert persisted_items[0].external_video_id == "first-item"


def test_delete_by_playlist_removes_snapshot_items() -> None:
    session = create_session()
    playlist = create_youtube_playlist(session)
    repository = YoutubePlaylistItemSqlAlchemyRepository(session)
    repository.replace_for_playlist(
        playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="to-delete",
                position=1,
                raw_title="Delete Me",
                raw_channel_name="Artist",
                normalized_title="delete me",
                normalized_artist="artist",
            )
        ],
    )

    repository.delete_by_playlist(playlist.id or 0)

    assert repository.list_by_playlist(playlist.id or 0) == []


def test_replace_for_playlist_keeps_relationship_with_youtube_playlist_model() -> None:
    session = create_session()
    playlist = create_youtube_playlist(session)
    repository = YoutubePlaylistItemSqlAlchemyRepository(session)
    repository.replace_for_playlist(
        playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=playlist.id or 0,
                external_video_id="related-item",
                position=1,
                raw_title="Related Song",
                raw_channel_name="Related Artist",
                normalized_title="related song",
                normalized_artist="related artist",
            )
        ],
    )

    persisted_model = session.query(YoutubePlaylistItemModel).one()

    assert persisted_model.youtube_playlist_id == playlist.id
    assert persisted_model.youtube_playlist is not None
    assert persisted_model.youtube_playlist.external_playlist_id == "PL123"
