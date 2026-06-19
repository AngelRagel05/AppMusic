from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application.use_cases import (
    CompareYoutubePlaylistWithLocalLibraryUseCase,
    ListPersistedPlaylistComparisonHistoryUseCase,
    LoadPersistedPlaylistComparisonUseCase,
    UpdatePlaylistComparisonResultUseCase,
)
from app.application.dto.updatePlaylistComparisonResultInputDto import (
    UpdatePlaylistComparisonResultInputDto,
)
from app.domain.library.entities.localSong import LocalSong
from app.domain.playlists.entities.playlistComparisonResult import PlaylistComparisonResult
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.services import (
    AUTO_NO_COMPETITIVE_CANDIDATE,
    MANUAL_USER_LINKED_LOCAL_SONG,
)
from app.infrastructure.persistence import (
    LocalFolderSqlAlchemyRepository,
    LocalSongSqlAlchemyRepository,
    PlaylistComparisonResultSqlAlchemyRepository,
    PlaylistComparisonSqlAlchemyRepository,
    YoutubePlaylistItemSqlAlchemyRepository,
    YoutubePlaylistSqlAlchemyRepository,
)
from app.presentation.features.comparison.comparisonResultFilter import (
    AUTOMATIC_COMPARISON_FILTER,
    MANUAL_COMPARISON_FILTER,
    filterComparisonItemsByStatus,
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
            title="song one",
            artist="artist one",
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
    assert result.summary.possible_match_count == 0
    assert result.summary.missing_count == 2
    assert result.summary.total_compared == 3
    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.FOUND,
        ComparisonStatus.MISSING,
        ComparisonStatus.MISSING,
    ]
    assert result.items[0].local_song_id is not None
    assert result.items[1].local_song_id is None
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
    assert persisted_comparison.youtube_playlist_state_fingerprint is not None
    assert persisted_comparison.youtube_playlist_state_fingerprint.startswith("youtube_playlist:")
    assert persisted_comparison.local_library_state_fingerprint is not None
    assert persisted_comparison.local_library_state_fingerprint.startswith("local_library:")
    assert [item.match_status for item in persisted_results] == [
        ComparisonStatus.FOUND.value,
        ComparisonStatus.MISSING.value,
        ComparisonStatus.MISSING.value,
    ]


def test_compare_youtube_playlist_with_local_library_use_case_uses_persisted_comparable_values() -> None:
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
            file_path=r"C:\Music\Active\song-one-deluxe.mp3",
            file_name="song-one-deluxe.mp3",
            is_available=True,
            title="song one",
            artist="artist one",
            duration_seconds=180.6,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="deluxe-item",
                position=1,
                raw_title="Artist One - Song One Deluxe",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert result.summary.found_count == 1
    assert result.summary.missing_count == 0
    assert result.items[0].comparison_status is ComparisonStatus.FOUND
    assert result.items[0].local_song_id is not None


def test_compare_youtube_playlist_with_local_library_use_case_marks_missing_when_title_exists_without_artist() -> None:
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
            file_path=r"C:\Music\Active\intro-otro-artista.mp3",
            file_name="intro-otro-artista.mp3",
            is_available=True,
            title="Intro",
            artist="Eazyboi",
            duration_seconds=180.0,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="intro-sfdk",
                position=1,
                raw_title="Intro",
                raw_channel_name="SFDK",
                normalized_title="intro",
                normalized_artist="sfdk",
                duration_seconds=180.0,
            )
        ],
    )

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert result.summary.found_count == 0
    assert result.summary.missing_count == 1
    assert result.items[0].comparison_status is ComparisonStatus.MISSING
    assert result.items[0].reason == "Existe titulo en local pero no artista valido."


def test_compare_youtube_playlist_with_local_library_use_case_excludes_reserved_found_song_from_later_items() -> None:
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
            file_path=r"C:\Music\Active\intro-sfdk.mp3",
            file_name="intro-sfdk.mp3",
            is_available=True,
            title="Intro",
            artist="SFDK",
            duration_seconds=180.0,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="intro-sfdk-1",
                position=1,
                raw_title="Intro",
                raw_channel_name="SFDK",
                normalized_title="intro",
                normalized_artist="sfdk",
                duration_seconds=180.0,
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="intro-sfdk-2",
                position=2,
                raw_title="Intro",
                raw_channel_name="SFDK",
                normalized_title="intro",
                normalized_artist="sfdk",
                duration_seconds=180.0,
            ),
        ],
    )

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.FOUND,
        ComparisonStatus.MISSING,
    ]
    assert result.items[0].local_song_id is not None
    assert [item.local_song_id for item in result.items if item.local_song_id is not None] == [
        result.items[0].local_song_id
    ]
    assert result.items[1].local_song_id is None
    assert result.items[1].reason == "La cancion local ya esta reservada por otro FOUND."


def test_compare_youtube_playlist_with_local_library_use_case_does_not_reserve_possible_matches() -> None:
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
            file_path=r"C:\Music\Active\song-one-a.mp3",
            file_name="song-one-a.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            duration_seconds=180.4,
        )
    )
    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one-b.mp3",
            file_name="song-one-b.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            duration_seconds=180.5,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="song-one-1",
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
                external_video_id="song-one-2",
                position=2,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            ),
        ],
    )

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.POSSIBLE_MATCH,
        ComparisonStatus.POSSIBLE_MATCH,
    ]


def test_compare_youtube_playlist_with_local_library_use_case_persists_observability_for_incremental_recompute() -> None:
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
    local_song_one = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="song one",
            artist="artist one",
            duration_seconds=180.0,
        )
    )
    local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-two.mp3",
            file_name="song-two.mp3",
            is_available=True,
            title="song two",
            artist="artist two",
            duration_seconds=200.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="frozen-found",
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
                external_video_id="recompute-item",
                position=2,
                raw_title="Song Two",
                raw_channel_name="Artist Two",
                normalized_title="song two",
                normalized_artist="artist two",
                duration_seconds=200.0,
            ),
        ],
    )
    previous_snapshot = playlist_comparison_repository.create(
        active_playlist.id or 0,
        active_folder.id or 0,
        youtube_playlist_imported_at=datetime(2100, 1, 1, 10, 0, tzinfo=UTC),
        local_library_scanned_at=datetime(2100, 1, 1, 10, 0, tzinfo=UTC),
        ignored_terms_version="ignored_terms:untracked",
        matching_rules_version=CompareYoutubePlaylistWithLocalLibraryUseCase.MATCHING_RULES_VERSION,
    )
    playlist_comparison_result_repository.save_for_comparison(
        previous_snapshot.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=previous_snapshot.id or 0,
                youtube_playlist_item_id=persisted_items[0].id or 0,
                local_song_id=local_song_one.id,
                match_status=ComparisonStatus.FOUND.value,
                score=100.0,
                matched_by="auto:title_artist_duration",
            ),
            PlaylistComparisonResult(
                playlist_comparison_id=previous_snapshot.id or 0,
                youtube_playlist_item_id=persisted_items[1].id or 0,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by=None,
            ),
        ],
    )
    playlist_comparison_repository.commit()

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert result.observability is not None
    assert result.observability.volume_metrics.skipped_found_count == 1
    assert result.observability.volume_metrics.reserved_local_song_count == 1
    assert result.observability.volume_metrics.recomputed_item_count == 1
    assert result.observability.volume_metrics.total_candidates_considered == 1
    assert result.observability.volume_metrics.average_candidates_per_recomputed_item == 1.0
    assert result.observability.phase_timings.total_seconds >= 0.0


def test_compare_youtube_playlist_with_local_library_use_case_invalidates_frozen_found_with_old_matching_rules_version() -> None:
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
    local_song_one = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="song one",
            artist="artist one",
            duration_seconds=180.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="frozen-found",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            ),
        ],
    )
    previous_snapshot = playlist_comparison_repository.create(
        active_playlist.id or 0,
        active_folder.id or 0,
        youtube_playlist_imported_at=datetime(2100, 1, 1, 10, 0, tzinfo=UTC),
        local_library_scanned_at=datetime(2100, 1, 1, 10, 0, tzinfo=UTC),
        ignored_terms_version="ignored_terms:untracked",
        matching_rules_version="persisted_match_v7_found_only_reservation_flow",
    )
    playlist_comparison_result_repository.save_for_comparison(
        previous_snapshot.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=previous_snapshot.id or 0,
                youtube_playlist_item_id=persisted_items[0].id or 0,
                local_song_id=local_song_one.id,
                match_status=ComparisonStatus.FOUND.value,
                score=100.0,
                matched_by="auto:title_artist_duration",
            ),
        ],
    )
    playlist_comparison_repository.commit()

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert result.summary.found_count == 1
    assert result.observability is not None
    assert result.observability.volume_metrics.skipped_found_count == 0
    assert result.observability.volume_metrics.recomputed_item_count == 1


def test_compare_youtube_playlist_with_local_library_use_case_keeps_frozen_found_reservation_for_later_rows() -> None:
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
    local_song_one = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\intro-sfdk.mp3",
            file_name="intro-sfdk.mp3",
            is_available=True,
            title="Intro",
            artist="SFDK",
            duration_seconds=180.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="frozen-found",
                position=1,
                raw_title="Intro",
                raw_channel_name="SFDK",
                normalized_title="intro",
                normalized_artist="sfdk",
                duration_seconds=180.0,
            ),
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="later-duplicate",
                position=2,
                raw_title="Intro",
                raw_channel_name="SFDK",
                normalized_title="intro",
                normalized_artist="sfdk",
                duration_seconds=180.0,
            ),
        ],
    )
    previous_snapshot = playlist_comparison_repository.create(
        active_playlist.id or 0,
        active_folder.id or 0,
        youtube_playlist_imported_at=datetime(2100, 1, 1, 10, 0, tzinfo=UTC),
        local_library_scanned_at=datetime(2100, 1, 1, 10, 0, tzinfo=UTC),
        ignored_terms_version="ignored_terms:untracked",
        matching_rules_version=CompareYoutubePlaylistWithLocalLibraryUseCase.MATCHING_RULES_VERSION,
    )
    playlist_comparison_result_repository.save_for_comparison(
        previous_snapshot.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=previous_snapshot.id or 0,
                youtube_playlist_item_id=persisted_items[0].id or 0,
                local_song_id=local_song_one.id,
                match_status=ComparisonStatus.FOUND.value,
                score=100.0,
                matched_by="auto:title_artist_duration",
            ),
            PlaylistComparisonResult(
                playlist_comparison_id=previous_snapshot.id or 0,
                youtube_playlist_item_id=persisted_items[1].id or 0,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by=None,
            ),
        ],
    )
    playlist_comparison_repository.commit()

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.FOUND,
        ComparisonStatus.MISSING,
    ]
    assert result.items[0].reason in (
        "Coincidencia FOUND conservada desde snapshot manual valido.",
        "Coincidencia FOUND conservada desde snapshot automatico valido.",
    )
    assert result.items[1].reason == "La cancion local ya esta reservada por otro FOUND."


def test_compare_youtube_playlist_with_local_library_use_case_keeps_nadal015_memories_i_regression_in_sqlalchemy() -> None:
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
            file_path=r"C:\Music\Active\memories-i.mp3",
            file_name="memories-i.mp3",
            is_available=True,
            title="memories i",
            artist="nadal015",
            duration_seconds=175.848,
        )
    )
    youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="nadal-015-memories-i",
                position=1,
                raw_title="NADAL 015 #MEMORIES I",
                raw_channel_name="NADAL 015",
                normalized_title="memories i",
                normalized_artist="nadal015",
                duration_seconds=176.0,
            )
        ],
    )

    result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert result.summary.found_count == 1
    assert result.items[0].comparison_status is ComparisonStatus.FOUND
    assert result.items[0].youtube_title == "NADAL 015 #MEMORIES I"


def test_youtube_playlist_item_repository_preserves_unchanged_item_identity_in_sqlalchemy() -> None:
    session = create_session()
    youtube_playlist_repository = YoutubePlaylistSqlAlchemyRepository(session)
    youtube_playlist_item_repository = YoutubePlaylistItemSqlAlchemyRepository(session)

    active_playlist = youtube_playlist_repository.save_as_active(
        "https://www.youtube.com/playlist?list=PL123",
        "PL123",
        "Favoritas",
    )

    first_snapshot = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="video-1",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )

    second_snapshot = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="video-1",
                position=1,
                raw_title="Song One",
                raw_channel_name="Artist One",
                normalized_title="song one",
                normalized_artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )

    assert second_snapshot[0].id == first_snapshot[0].id
    assert second_snapshot[0].created_at == first_snapshot[0].created_at
    assert second_snapshot[0].updated_at == first_snapshot[0].updated_at


def test_update_playlist_comparison_result_use_case_updates_real_repository_row() -> None:
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
    manual_local_song = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\manual-link.mp3",
            file_name="manual-link.mp3",
            is_available=True,
            title="Different Local Track",
            artist="Local Artist",
            duration_seconds=210.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="missing-item",
                position=1,
                raw_title="Impossible To Match Automatically",
                raw_channel_name="Youtube Artist",
                normalized_title="impossible to match automatically",
                normalized_artist="youtube artist",
                duration_seconds=180.0,
            )
        ],
    )

    comparison_result = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()
    latest_comparison = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )

    if latest_comparison is None or latest_comparison.id is None:
        raise AssertionError("Se esperaba una comparacion persistida.")

    original_row = playlist_comparison_result_repository.find_by_comparison_item(
        latest_comparison.id,
        persisted_items[0].id or 0,
    )
    if original_row is None:
        raise AssertionError("Se esperaba un resultado persistido para editar.")

    updated_row = UpdatePlaylistComparisonResultUseCase(
        playlist_comparison_repository,
        playlist_comparison_result_repository,
        local_song_repository,
    ).execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=latest_comparison.id,
            youtube_playlist_item_id=persisted_items[0].id or 0,
            match_status=ComparisonStatus.FOUND.value,
            local_song_id=manual_local_song.id,
        )
    )

    reloaded_row = playlist_comparison_result_repository.find_by_comparison_item(
        latest_comparison.id,
        persisted_items[0].id or 0,
    )

    assert comparison_result.items[0].comparison_status is ComparisonStatus.MISSING
    assert original_row.match_status == ComparisonStatus.MISSING.value
    assert updated_row.local_song_id == manual_local_song.id
    assert updated_row.match_status == ComparisonStatus.FOUND.value
    assert updated_row.score == original_row.score
    assert updated_row.matched_by == MANUAL_USER_LINKED_LOCAL_SONG
    assert reloaded_row is not None
    assert reloaded_row.local_song_id == manual_local_song.id
    assert reloaded_row.match_status == ComparisonStatus.FOUND.value
    assert reloaded_row.matched_by == MANUAL_USER_LINKED_LOCAL_SONG


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
            title="song one",
            artist="artist one",
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


def test_load_persisted_playlist_comparison_use_case_rehydrates_legacy_snapshot_without_fingerprint_columns() -> None:
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
    local_song = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="song one",
            artist="artist one",
            duration_seconds=181.0,
        )
    )
    persisted_item = youtube_playlist_item_repository.replace_for_playlist(
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
    )[0]

    legacy_comparison = playlist_comparison_repository.create(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    playlist_comparison_result_repository.save_for_comparison(
        legacy_comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=legacy_comparison.id or 0,
                youtube_playlist_item_id=persisted_item.id or 0,
                local_song_id=local_song.id,
                match_status=ComparisonStatus.FOUND.value,
                score=100.0,
                matched_by="auto:title_artist_duration",
            )
        ],
    )
    session.commit()

    rehydrated_snapshot = LoadPersistedPlaylistComparisonUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert rehydrated_snapshot is not None
    _, comparison_result = rehydrated_snapshot
    assert comparison_result.items[0].comparison_status is ComparisonStatus.FOUND
    assert comparison_result.items[0].local_song_id == local_song.id


def test_load_persisted_playlist_comparison_use_case_restores_manual_override_from_persisted_snapshot() -> None:
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
    manual_local_song = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\manual-link.mp3",
            file_name="manual-link.mp3",
            is_available=True,
            title="Different Local Track",
            artist="Local Artist",
            duration_seconds=210.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="missing-item",
                position=1,
                raw_title="Impossible To Match Automatically",
                raw_channel_name="Youtube Artist",
                normalized_title="impossible to match automatically",
                normalized_artist="youtube artist",
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
    latest_comparison = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    if latest_comparison is None or latest_comparison.id is None:
        raise AssertionError("Se esperaba una comparacion persistida.")

    UpdatePlaylistComparisonResultUseCase(
        playlist_comparison_repository,
        playlist_comparison_result_repository,
        local_song_repository,
    ).execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=latest_comparison.id,
            youtube_playlist_item_id=persisted_items[0].id or 0,
            match_status=ComparisonStatus.FOUND.value,
            local_song_id=manual_local_song.id,
        )
    )

    persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert persisted_snapshot is not None
    _, comparison_result = persisted_snapshot
    assert comparison_result.items[0].comparison_status is ComparisonStatus.FOUND
    assert comparison_result.items[0].local_song_id == manual_local_song.id
    assert comparison_result.items[0].local_title == "Different Local Track"
    assert comparison_result.items[0].local_artist == "Local Artist"
    assert comparison_result.items[0].matched_by == MANUAL_USER_LINKED_LOCAL_SONG
    assert (
        comparison_result.items[0].reason
        == "Enlace manual con cancion local decidido por el usuario."
    )


def test_compare_youtube_playlist_with_local_library_use_case_keeps_valid_manual_found_frozen_in_new_snapshot() -> None:
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
    manual_local_song = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\manual-link.mp3",
            file_name="manual-link.mp3",
            is_available=True,
            title="Different Local Track",
            artist="Local Artist",
            duration_seconds=210.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="missing-item",
                position=1,
                raw_title="Impossible To Match Automatically",
                raw_channel_name="Youtube Artist",
                normalized_title="impossible to match automatically",
                normalized_artist="youtube artist",
                duration_seconds=180.0,
            )
        ],
    )
    compare_use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    )

    compare_use_case.execute()
    first_snapshot = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    if first_snapshot is None or first_snapshot.id is None:
        raise AssertionError("Se esperaba una comparacion persistida.")

    UpdatePlaylistComparisonResultUseCase(
        playlist_comparison_repository,
        playlist_comparison_result_repository,
        local_song_repository,
    ).execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=first_snapshot.id,
            youtube_playlist_item_id=persisted_items[0].id or 0,
            match_status=ComparisonStatus.FOUND.value,
            local_song_id=manual_local_song.id,
        )
    )

    rerun_result = compare_use_case.execute()
    latest_snapshot = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    if latest_snapshot is None or latest_snapshot.id is None:
        raise AssertionError("Se esperaba una nueva comparacion persistida.")

    manual_row = playlist_comparison_result_repository.find_by_comparison_item(
        first_snapshot.id,
        persisted_items[0].id or 0,
    )
    recalculated_row = playlist_comparison_result_repository.find_by_comparison_item(
        latest_snapshot.id,
        persisted_items[0].id or 0,
    )

    assert latest_snapshot.id != first_snapshot.id
    assert manual_row is not None
    assert manual_row.match_status == ComparisonStatus.FOUND.value
    assert manual_row.local_song_id == manual_local_song.id
    assert manual_row.matched_by == MANUAL_USER_LINKED_LOCAL_SONG
    assert rerun_result.items[0].comparison_status is ComparisonStatus.FOUND
    assert rerun_result.items[0].local_song_id == manual_local_song.id
    assert recalculated_row is not None
    assert recalculated_row.match_status == ComparisonStatus.FOUND.value
    assert recalculated_row.local_song_id == manual_local_song.id
    assert recalculated_row.matched_by == MANUAL_USER_LINKED_LOCAL_SONG


def test_load_persisted_playlist_comparison_use_case_supports_manual_and_automatic_filters_after_reload() -> None:
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
            title="song one",
            artist="artist one",
            duration_seconds=181.0,
        )
    )
    manual_local_song = local_song_repository.save(
        LocalSong(
            local_folder_id=active_folder.id,
            file_path=r"C:\Music\Active\manual-link.mp3",
            file_name="manual-link.mp3",
            is_available=True,
            title="Different Local Track",
            artist="Local Artist",
            duration_seconds=210.0,
        )
    )
    persisted_items = youtube_playlist_item_repository.replace_for_playlist(
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
                external_video_id="missing-item",
                position=2,
                raw_title="Impossible To Match Automatically",
                raw_channel_name="Youtube Artist",
                normalized_title="impossible to match automatically",
                normalized_artist="youtube artist",
                duration_seconds=180.0,
            ),
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
    latest_comparison = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    if latest_comparison is None or latest_comparison.id is None:
        raise AssertionError("Se esperaba una comparacion persistida.")

    UpdatePlaylistComparisonResultUseCase(
        playlist_comparison_repository,
        playlist_comparison_result_repository,
        local_song_repository,
    ).execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=latest_comparison.id,
            youtube_playlist_item_id=persisted_items[1].id or 0,
            match_status=ComparisonStatus.FOUND.value,
            local_song_id=manual_local_song.id,
        )
    )

    persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert persisted_snapshot is not None
    _, comparison_result = persisted_snapshot
    manual_items = filterComparisonItemsByStatus(
        comparison_result.items,
        MANUAL_COMPARISON_FILTER,
    )
    automatic_items = filterComparisonItemsByStatus(
        comparison_result.items,
        AUTOMATIC_COMPARISON_FILTER,
    )

    assert [item.youtube_playlist_item_id for item in manual_items] == [
        persisted_items[1].id or 0
    ]
    assert [item.youtube_playlist_item_id for item in automatic_items] == [
        persisted_items[0].id or 0
    ]
    assert manual_items[0].matched_by == MANUAL_USER_LINKED_LOCAL_SONG
    assert automatic_items[0].matched_by is not None


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
            title="song one",
            artist="artist one",
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


def test_playlist_comparison_repositories_support_retention_operations_by_scope() -> None:
    session = create_session()
    playlist_comparison_repository = PlaylistComparisonSqlAlchemyRepository(session)
    playlist_comparison_result_repository = PlaylistComparisonResultSqlAlchemyRepository(session)

    first = playlist_comparison_repository.create(9, 7)
    second = playlist_comparison_repository.create(9, 7)
    third = playlist_comparison_repository.create(9, 7)
    fourth = playlist_comparison_repository.create(9, 7)
    other_scope = playlist_comparison_repository.create(9, 8)

    playlist_comparison_result_repository.save_for_comparison(
        first.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=first.id or 0,
                youtube_playlist_item_id=1,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by=None,
            )
        ],
    )
    session.commit()

    excess = playlist_comparison_repository.list_excess_for_scope(9, 7, keep_latest=3)

    assert [comparison.id for comparison in excess] == [first.id]

    playlist_comparison_result_repository.delete_by_comparison_id(first.id or 0)
    playlist_comparison_repository.delete_by_ids([first.id or 0])
    session.commit()

    assert playlist_comparison_result_repository.list_by_comparison(first.id or 0) == []
    remaining_scope = playlist_comparison_repository.list_for_scope(9, 7, limit=10)
    assert [comparison.id for comparison in remaining_scope] == [
        fourth.id,
        third.id,
        second.id,
    ]
    other_scope_latest = playlist_comparison_repository.find_latest_for_scope(9, 8)
    assert other_scope_latest is not None
    assert other_scope_latest.id == other_scope.id


def test_playlist_comparison_repository_roundtrips_snapshot_metadata() -> None:
    session = create_session()
    repository = PlaylistComparisonSqlAlchemyRepository(session)

    created_comparison = repository.create(
        9,
        7,
        youtube_playlist_imported_at=datetime(2026, 6, 16, 10, 0, tzinfo=UTC),
        local_library_scanned_at=datetime(2026, 6, 16, 10, 5, tzinfo=UTC),
        youtube_playlist_state_fingerprint="youtube_playlist:abc123",
        local_library_state_fingerprint="local_library:def456",
        ignored_terms_version="ignored_terms:ghi789",
        matching_rules_version="persisted_match_v6_schema",
    )
    repository.commit()

    reloaded_comparison = repository.find_by_id(created_comparison.id or 0)

    assert reloaded_comparison is not None
    assert reloaded_comparison.youtube_playlist_imported_at == datetime(
        2026, 6, 16, 10, 0, tzinfo=UTC
    )
    assert reloaded_comparison.local_library_scanned_at == datetime(
        2026, 6, 16, 10, 5, tzinfo=UTC
    )
    assert reloaded_comparison.youtube_playlist_state_fingerprint == "youtube_playlist:abc123"
    assert reloaded_comparison.local_library_state_fingerprint == "local_library:def456"
    assert reloaded_comparison.ignored_terms_version == "ignored_terms:ghi789"
    assert reloaded_comparison.matching_rules_version == "persisted_match_v6_schema"


def test_compare_youtube_playlist_with_local_library_use_case_retains_only_three_snapshots_per_scope() -> None:
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
            title="song one",
            artist="artist one",
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

    other_scope = playlist_comparison_repository.create(active_playlist.id or 0, 99)
    playlist_comparison_result_repository.save_for_comparison(
        other_scope.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=other_scope.id or 0,
                youtube_playlist_item_id=999,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by=None,
            )
        ],
    )
    playlist_comparison_repository.commit()

    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    )

    first_snapshot_id: int | None = None
    last_result = None
    for iteration in range(4):
        last_result = use_case.execute()
        latest = playlist_comparison_repository.find_latest_for_scope(
            active_playlist.id or 0,
            active_folder.id or 0,
        )
        if iteration == 0:
            first_snapshot_id = latest.id if latest is not None else None

    if first_snapshot_id is None:
        raise AssertionError("Se esperaba capturar el primer snapshot persistido.")
    if last_result is None:
        raise AssertionError("Se esperaba el resultado de la ultima comparacion.")

    retained_scope = playlist_comparison_repository.list_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
        limit=10,
    )
    latest_persisted = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    history = ListPersistedPlaylistComparisonHistoryUseCase(
        youtube_playlist_repository,
        local_folder_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute(limit=5)
    persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
        youtube_playlist_repository,
        youtube_playlist_item_repository,
        local_folder_repository,
        local_song_repository,
        playlist_comparison_repository,
        playlist_comparison_result_repository,
    ).execute()

    assert len(retained_scope) == 3
    assert [comparison.id for comparison in retained_scope] == [5, 4, 3]
    assert latest_persisted is not None
    assert latest_persisted.id == retained_scope[0].id
    assert last_result.last_compared_at is not None
    assert latest_persisted.compared_at is not None
    assert last_result.last_compared_at == latest_persisted.compared_at
    assert playlist_comparison_result_repository.list_by_comparison(first_snapshot_id) == []
    remaining_results = session.query(PlaylistComparisonResultModel).all()
    assert all(
        result.playlist_comparison_id != first_snapshot_id for result in remaining_results
    )
    assert len(history) == 3
    assert [entry.comparison_id for entry in history] == [5, 4, 3]
    assert persisted_snapshot is not None
    loaded_local_songs, loaded_comparison_result = persisted_snapshot
    assert len(loaded_local_songs) == 1
    assert loaded_comparison_result.summary.total_compared == 1
    assert loaded_comparison_result.items[0].comparison_status is ComparisonStatus.FOUND
    assert loaded_comparison_result.last_compared_at is not None
    assert loaded_comparison_result.last_compared_at == latest_persisted.compared_at
    other_scope_latest = playlist_comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        99,
    )
    assert other_scope_latest is not None
    assert other_scope_latest.id == other_scope.id


def test_playlist_comparison_retention_only_purges_exact_scope_in_sqlalchemy() -> None:
    session = create_session()
    playlist_comparison_repository = PlaylistComparisonSqlAlchemyRepository(session)
    playlist_comparison_result_repository = PlaylistComparisonResultSqlAlchemyRepository(session)

    same_scope_first = playlist_comparison_repository.create(9, 7)
    same_scope_second = playlist_comparison_repository.create(9, 7)
    same_scope_third = playlist_comparison_repository.create(9, 7)
    same_scope_fourth = playlist_comparison_repository.create(9, 7)
    same_playlist_other_folder = playlist_comparison_repository.create(9, 8)
    other_playlist_same_folder = playlist_comparison_repository.create(10, 7)

    for comparison in (
        same_scope_first,
        same_scope_second,
        same_scope_third,
        same_scope_fourth,
        same_playlist_other_folder,
        other_playlist_same_folder,
    ):
        playlist_comparison_result_repository.save_for_comparison(
            comparison.id or 0,
            [
                PlaylistComparisonResult(
                    playlist_comparison_id=comparison.id or 0,
                    youtube_playlist_item_id=(comparison.id or 0) * 10,
                    local_song_id=None,
                    match_status=ComparisonStatus.MISSING.value,
                    score=0.0,
                    matched_by=None,
                )
            ],
        )

    excess = playlist_comparison_repository.list_excess_for_scope(9, 7, keep_latest=3)
    excess_ids = [comparison.id for comparison in excess if comparison.id is not None]
    for comparison_id in excess_ids:
        playlist_comparison_result_repository.delete_by_comparison_id(comparison_id)
    playlist_comparison_repository.delete_by_ids(excess_ids)
    playlist_comparison_repository.commit()

    retained_same_scope = playlist_comparison_repository.list_for_scope(9, 7, limit=10)
    assert [comparison.id for comparison in retained_same_scope] == [
        same_scope_fourth.id,
        same_scope_third.id,
        same_scope_second.id,
    ]
    latest_same_scope = playlist_comparison_repository.find_latest_for_scope(9, 7)
    assert latest_same_scope is not None
    assert latest_same_scope.id == same_scope_fourth.id
    assert playlist_comparison_result_repository.list_by_comparison(same_scope_first.id or 0) == []
    assert playlist_comparison_result_repository.list_by_comparison(same_scope_fourth.id or 0) != []

    same_playlist_other_folder_latest = playlist_comparison_repository.find_latest_for_scope(9, 8)
    assert same_playlist_other_folder_latest is not None
    assert same_playlist_other_folder_latest.id == same_playlist_other_folder.id
    other_playlist_same_folder_latest = playlist_comparison_repository.find_latest_for_scope(10, 7)
    assert other_playlist_same_folder_latest is not None
    assert other_playlist_same_folder_latest.id == other_playlist_same_folder.id
    assert (
        playlist_comparison_result_repository.list_by_comparison(
            same_playlist_other_folder.id or 0
        )
        != []
    )
    assert (
        playlist_comparison_result_repository.list_by_comparison(
            other_playlist_same_folder.id or 0
        )
        != []
    )
