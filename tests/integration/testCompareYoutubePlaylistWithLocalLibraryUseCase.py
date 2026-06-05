from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application.use_cases import CompareYoutubePlaylistWithLocalLibraryUseCase
from app.domain.library.entities.localSong import LocalSong
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.infrastructure.persistence import (
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
    YoutubePlaylistItemSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.infrastructure.persistence.database.base import Base
from app.shared.constants.comparison import ComparisonStatus


def create_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(bind=engine)


def test_compare_youtube_playlist_with_local_library_use_case_matches_real_repositories() -> None:
    session = create_session()
    local_folder_repository = LocalFolderSqlAlchemyRepository(session)
    local_song_repository = LocalSongSqlAlchemyRepository(session)
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
