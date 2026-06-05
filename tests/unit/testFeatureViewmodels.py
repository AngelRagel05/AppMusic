from __future__ import annotations

from collections.abc import Callable

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.viewmodels.comparison.libraryComparisonViewModel import (
    LibraryComparisonFeedback,
    LibraryComparisonViewModel,
)
from app.presentation.viewmodels.ignoredTerms.ignoredTermsViewModel import (
    IgnoredTermsViewModel,
)
from app.presentation.viewmodels.localLibrary.localFolderViewModel import (
    LocalFolderViewModel,
)
from app.presentation.viewmodels.youtubePlaylists.youtubePlaylistViewModel import (
    YoutubePlaylistViewModel,
)
from app.shared.constants.comparison import ComparisonStatus


class StubUseCase:
    def __init__(self, result=None) -> None:
        self.result = result
        self.calls: list[object] = []

    def execute(self, payload=None):
        self.calls.append(payload)
        return self.result


def runScheduledCallbacks(callbacks: list[Callable[[], None]]) -> None:
    for callback in callbacks:
        callback()


def test_local_folder_view_model_refresh_state_caches_collection_and_active_folder() -> None:
    active_folder = LocalFolderDto(
        id=2,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    folders = [
        LocalFolderDto(
            id=1,
            path=r"C:\Music\One",
            display_name="One",
            is_active=False,
        ),
        active_folder,
    ]
    list_use_case = StubUseCase(folders)
    get_active_use_case = StubUseCase(active_folder)
    view_model = LocalFolderViewModel(
        list_use_case=list_use_case,
        get_active_use_case=get_active_use_case,
        activate_use_case=StubUseCase(active_folder),
        define_main_use_case=StubUseCase(active_folder),
        update_use_case=StubUseCase(active_folder),
        delete_use_case=StubUseCase(None),
    )

    loaded_folders, loaded_active_folder = view_model.refreshState()

    assert loaded_folders == folders
    assert loaded_active_folder == active_folder
    assert view_model.load_folders() == folders
    assert view_model.load_active_folder() == active_folder
    assert view_model.find_folder_by_id(2) == active_folder
    assert len(list_use_case.calls) == 1
    assert len(get_active_use_case.calls) == 1


def test_youtube_playlist_view_model_activate_playlist_refreshes_cached_state() -> None:
    initial_active = YoutubePlaylistDto(
        id=1,
        playlist_url="https://www.youtube.com/playlist?list=PLONE",
        external_playlist_id="PLONE",
        title="One",
        is_active=True,
    )
    activated_playlist = YoutubePlaylistDto(
        id=2,
        playlist_url="https://www.youtube.com/playlist?list=PLTWO",
        external_playlist_id="PLTWO",
        title="Two",
        is_active=True,
    )
    list_use_case = StubUseCase([activated_playlist, initial_active])
    get_active_use_case = StubUseCase(activated_playlist)
    activate_use_case = StubUseCase(activated_playlist)
    view_model = YoutubePlaylistViewModel(
        list_use_case=list_use_case,
        get_active_use_case=get_active_use_case,
        activate_use_case=activate_use_case,
        define_main_use_case=StubUseCase(activated_playlist),
        update_use_case=StubUseCase(activated_playlist),
        delete_use_case=StubUseCase(None),
    )

    returned_playlist = view_model.activate_playlist(2)

    assert returned_playlist == activated_playlist
    assert view_model.load_active_playlist() == activated_playlist
    assert view_model.find_playlist_by_id(2) == activated_playlist
    assert len(activate_use_case.calls) == 1
    assert len(list_use_case.calls) == 1
    assert len(get_active_use_case.calls) == 1


def test_ignored_terms_view_model_create_term_refreshes_cached_terms() -> None:
    created_term = IgnoredTermDto(
        id=4,
        term="live",
        scope="title",
        language="global",
        is_active=True,
    )
    list_use_case = StubUseCase([created_term])
    create_use_case = StubUseCase(created_term)
    view_model = IgnoredTermsViewModel(
        list_use_case=list_use_case,
        create_use_case=create_use_case,
        update_use_case=StubUseCase(created_term),
        delete_use_case=StubUseCase(None),
    )

    returned_term = view_model.create_term("live", "title", "global")

    assert returned_term == created_term
    assert view_model.load_terms() == [created_term]
    assert view_model.find_term_by_id(4) == created_term
    assert len(create_use_case.calls) == 1
    assert len(list_use_case.calls) == 1


def test_library_comparison_view_model_emits_start_and_success_feedback() -> None:
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=2,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            album="Album One",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.0,
        )
    ]
    comparison_result = PlaylistComparisonResultDto(
        summary=PlaylistComparisonSummaryDto(
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        ),
        items=[
            PlaylistComparisonItemResultDto(
                youtube_playlist_item_id=1,
                local_song_id=1,
                comparison_status=ComparisonStatus.FOUND,
                youtube_title="Song One",
                youtube_artist="Artist One",
                local_title="Song One",
                local_artist="Artist One",
                score=99.0,
                reason="Coincidencia fuerte.",
            )
        ],
    )
    local_songs_use_case = StubUseCase(local_songs)
    compare_use_case = StubUseCase(comparison_result)
    view_model = LibraryComparisonViewModel(
        load_library_comparison=lambda: (
            local_songs_use_case.execute(),
            compare_use_case.execute(),
        ),
    )
    feedbacks: list[LibraryComparisonFeedback] = []
    scheduled_callbacks: list[Callable[[], None]] = []

    view_model.requestComparison(
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=feedbacks.append,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert view_model.load_local_songs() == local_songs
    assert view_model.load_comparison_result() == comparison_result
    assert len(local_songs_use_case.calls) == 1
    assert len(compare_use_case.calls) == 1
    assert feedbacks == [
        LibraryComparisonFeedback(
            status_message="Comparando biblioteca local contra playlist activa...",
            status_tone="info",
            local_songs=None,
            comparison_result=None,
            last_action_message=None,
        ),
        LibraryComparisonFeedback(
            status_message="Comparacion completada: 1 encontradas, 0 posibles coincidencias y 0 faltan.",
            status_tone="success",
            local_songs=local_songs,
            comparison_result=comparison_result,
            last_action_message="Comparacion completada: 1 encontradas, 0 posibles coincidencias y 0 faltan.",
        ),
    ]


def test_library_comparison_view_model_invalidates_cached_comparison_until_next_success() -> None:
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=2,
            file_path=r"C:\Music\Active\song-one.mp3",
            file_name="song-one.mp3",
            is_available=True,
            title="Song One",
            artist="Artist One",
            album="Album One",
            release_year=2024,
            track_number_album=1,
            duration_seconds=180.0,
        )
    ]
    comparison_result = PlaylistComparisonResultDto(
        summary=PlaylistComparisonSummaryDto(
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        ),
        items=[],
    )
    view_model = LibraryComparisonViewModel(
        load_library_comparison=lambda: (
            StubUseCase(local_songs).execute(),
            StubUseCase(comparison_result).execute(),
        ),
    )
    scheduled_callbacks: list[Callable[[], None]] = []

    assert view_model.isComparisonStale() is True
    assert view_model.hasCachedComparison() is False

    view_model.requestComparison(
        schedule_on_main_thread=scheduled_callbacks.append,
        on_feedback=lambda _feedback: None,
    )
    runScheduledCallbacks(scheduled_callbacks)

    assert view_model.hasCachedComparison() is True
    assert view_model.isComparisonStale() is False

    view_model.invalidateComparison()

    assert view_model.isComparisonStale() is True
