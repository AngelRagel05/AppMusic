from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application.use_cases import (
    CompareYoutubePlaylistWithLocalLibraryUseCase,
    ListPersistedPlaylistComparisonHistoryUseCase,
    LoadPersistedPlaylistComparisonUseCase,
)
from app.domain.library.entities.localSong import LocalSong
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.infrastructure.persistence import (
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
    PlaylistComparisonResultSqlAlchemyRepository,
    PlaylistComparisonSqlAlchemyRepository,
    YoutubePlaylistItemSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.models import (
    PlaylistComparison as PlaylistComparisonModel,
    PlaylistComparisonResult as PlaylistComparisonResultModel,
)
from app.shared.constants.comparison import ComparisonStatus


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def test_compare_youtube_playlist_with_local_library_use_case_matches_real_repositories() -> None:
    session = create_session()
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    playlist_comparison_repository = PlaylistComparisonSqlAlchemyRepository(session)
    playlist_comparison_result_repository = PlaylistComparisonResultSqlAlchemyRepository(session)
    youtube_playlist_repository = YoutubePlaylistSqlAlchemyRepository(session)
    youtube_playlist_item_repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    active_folder = local_folder_repository.save_as_active(r"C:\Music\Active", "Active")
    active_playlist = youtube_playlist_repository.save_as_active(
        "https://www.youtube.com/playlist?list=PL123",
        "PL123",
        "Favoritas",
    )

    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            duration_seconds=181.0,
        )
    )
    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-two-live.mp3",
            file_name="song-two-live.mp3",
            is_available=True,
            title="Song Two Live",
            artist="Artist Two Remix",
            duration_seconds=200.0,
        )
    )
    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\missing-song.mp3",
            file_name="missing-song.mp3",
            is_available=False,
            title="Missing Song",
            artist="Missing Artist",
            duration_seconds=240.0,
        )
    )

    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="found-item",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="possible-item",
                position=2,
                raw_title="Song Two",
                raw_channel_name="Artist Two",
                normalized_title="song two",
                normalized_artist="artist two",
                duration_seconds=200.0,
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="missing-item",
                position=3,
                raw_title="Missing Song",
                raw_channel_name="Missing Artist",
                normalized_title="missing song",
                normalized_artist="missing artist",
                duration_seconds=240.0,
            ),
        ],
    )

    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    )

    result = use_case.execute()

    assert result.summary.found_count == 1
    assert result.summary.possible_match_count == 1
    assert result.summary.missing_count == 1
    assert result.summary.total_compared == 3
    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.FOUND,
        ComparisonStatus.POSSIBLE_MATCH,
        ComparisonStatus.MISSING,
    ]
    assert result.items[0].local_song_id is not None
    assert result.items[1].local_song_id is not None
    assert result.items[2].local_song_id is None
    persisted_comparison = session.query(PlaylistComparisonModel).one()
    persisted_results = (
        session.query(PlaylistComparisonResultModel)
        .filter(PlaylistComparisonResultModel.playlist_comparison_id == persisted_comparison.id)
        .order_by(PlaylistComparisonResultModel.youtube_playlist_item_id.asc())
        .all()
    )
    assert len(persisted_results) == 3
    assert persisted_results[0].score == result.items[0].score
    assert persisted_results[1].score == result.items[1].score
    assert persisted_results[2].score == result.items[2].score
    assert [item.match_status for item in persisted_results] == [
        ComparisonStatus.FOUND.value,
        ComparisonStatus.POSSIBLE_MATCH.value,
        ComparisonStatus.MISSING.value,
    ]


def test_load_persisted_playlist_comparison_use_case_restores_last_saved_snapshot() -> None:
    session = create_session()
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    playlist_comparison_repository = PlaylistComparisonSqlAlchemyRepository(session)
    playlist_comparison_result_repository = PlaylistComparisonResultSqlAlchemyRepository(session)
    youtube_playlist_repository = YoutubePlaylistSqlAlchemyRepository(session)
    youtube_playlist_item_repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    active_folder = local_folder_repository.save_as_active(r"C:\Music\Active", "Active")
    active_playlist = youtube_playlist_repository.save_as_active(
        "https://www.youtube.com/playlist?list=PL123",
        "PL123",
        "Favoritas",
    )

    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            duration_seconds=181.0,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="found-item",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )

    CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert persisted_snapshot is not None
    local_songs, comparison_result = persisted_snapshot
    assert len(local_songs) == 1
    assert comparison_result.summary.found_count == 1
    assert comparison_result.summary.total_compared == 1
    assert comparison_result.items[0].comparison_status is ComparisonStatus.FOUND
    assert comparison_result.items[0].score > 0


def test_list_persisted_playlist_comparison_history_use_case_returns_latest_runs_for_active_scope() -> None:
    session = create_session()
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
    playlist_comparison_repository = PlaylistComparisonSqlAlchemyRepository(session)
    playlist_comparison_result_repository = PlaylistComparisonResultSqlAlchemyRepository(session)
    youtube_playlist_repository = YoutubePlaylistSqlAlchemyRepository(session)
    youtube_playlist_item_repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    active_folder = local_folder_repository.save_as_active(r"C:\Music\Active", "Active")
    active_playlist = youtube_playlist_repository.save_as_active(
        "https://www.youtube.com/playlist?list=PL123",
        "PL123",
        "Favoritas",
    )

    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            duration_seconds=181.0,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="found-item",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )

    CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()
    first_comparison = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    if first_comparison is None or first_comparison.id is None:
        raise AssertionError("Se esperaba la primera comparacion persistida.")

    first_model = session.query(PlaylistComparisonModel).filter_by(id=first_comparison.id).one()
    first_model.compared_at = datetime(2026, 6, 8, 8, 0, tzinfo=UTC)
    session.flush()

    CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()
    second_comparison = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    if second_comparison is None or second_comparison.id is None:
        raise AssertionError("Se esperaba la segunda comparacion persistida.")

    second_model = session.query(PlaylistComparisonModel).filter_by(id=second_comparison.id).one()
    second_model.compared_at = datetime(2026, 6, 8, 9, 0, tzinfo=UTC)
    session.flush()

    history = ListPersistedPlaylistComparisonHistoryUseCase(
        youtube_playlist_repository,
        local_folder_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute(limit=5)

    assert [entry.comparison_id for entry in history] == [second_comparison.id, first_comparison.id]
    assert history[0].compared_at == datetime(2026, 6, 8, 9, 0, tzinfo=UTC)
    assert history[0].found_count == 1
    assert history[0].total_compared == 1
