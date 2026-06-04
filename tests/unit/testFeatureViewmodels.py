from __future__ import annotations

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.youtubePlaylistItemDto import YoutubePlaylistItemDto
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.viewmodels.comparison.libraryComparisonViewModel import (
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


class StubUseCase:
    def __init__(self, result=None) -> None:
        self.result = result
        self.calls: list[object] = []

    def execute(self, payload=None):
        self.calls.append(payload)
        return self.result


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


def test_library_comparison_view_model_refresh_state_caches_both_lists() -> None:
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
    youtube_playlist_items = [
        YoutubePlaylistItemDto(
            id=1,
            youtube_playlist_id=5,
            external_video_id="abc123",
            position=1,
            raw_title="Song One",
            raw_channel_name="Artist One",
            normalized_title="song one",
            normalized_artist="artist one",
            duration_seconds=180.0,
        )
    ]
    local_songs_use_case = StubUseCase(local_songs)
    youtube_items_use_case = StubUseCase(youtube_playlist_items)
    view_model = LibraryComparisonViewModel(
        list_active_local_songs_use_case=local_songs_use_case,
        list_active_youtube_playlist_items_use_case=youtube_items_use_case,
    )

    loaded_local_songs, loaded_youtube_playlist_items = view_model.refreshState()

    assert loaded_local_songs == local_songs
    assert loaded_youtube_playlist_items == youtube_playlist_items
    assert view_model.load_local_songs() == local_songs
    assert view_model.load_youtube_playlist_items() == youtube_playlist_items
    assert len(local_songs_use_case.calls) == 1
    assert len(youtube_items_use_case.calls) == 1
