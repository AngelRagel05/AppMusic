from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.activateYoutubePlaylistInputDto import (
    ActivateYoutubePlaylistInputDto,
)
from app.application.dto.deleteYoutubePlaylistInputDto import (
    DeleteYoutubePlaylistInputDto,
)
from app.application.dto.defineMainYoutubePlaylistInputDto import (
    DefineMainYoutubePlaylistInputDto,
)
from app.application.dto.importedYoutubePlaylistItemDto import ImportedYoutubePlaylistItemDto
from app.application.dto.updateYoutubePlaylistInputDto import (
    UpdateYoutubePlaylistInputDto,
)
from app.application.use_cases import (
    ActivateYoutubePlaylistUseCase,
    CompareYoutubePlaylistWithLocalLibraryUseCase,
    DefineMainYoutubePlaylistUseCase,
    DeleteYoutubePlaylistUseCase,
    GetActiveYoutubePlaylistUseCase,
    ImportYoutubePlaylistItemsUseCase,
    ListPersistedPlaylistComparisonHistoryUseCase,
    ListActiveYoutubePlaylistItemsUseCase,
    LoadPersistedPlaylistComparisonUseCase,
    ListYoutubePlaylistsUseCase,
    UpdatePlaylistComparisonResultUseCase,
    UpdateYoutubePlaylistUseCase,
)
from app.application.dto.updatePlaylistComparisonResultInputDto import (
    UpdatePlaylistComparisonResultInputDto,
)
from app.application.use_cases.playlists.youtubePlaylistItemsImporterPort import (
    YoutubePlaylistImportExtractorError,
)
from app.domain.filters.entities.ignoredTerm import IgnoredTerm
from app.domain.filters.repositories.ignoredTermRepository import IgnoredTermRepository
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.playlists.entities.youtubePlaylist import YoutubePlaylist
from app.domain.playlists.entities.playlistComparison import PlaylistComparison
from app.domain.playlists.entities.playlistComparisonResult import PlaylistComparisonResult
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.repositories.playlistComparisonRepository import (
    PlaylistComparisonRepository,
)
from app.domain.playlists.repositories.playlistComparisonResultRepository import (
    PlaylistComparisonResultRepository,
)
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.playlists.services import (
    AUTO_NO_COMPETITIVE_CANDIDATE,
    AUTO_TITLE_ARTIST_DURATION,
    MANUAL_USER_LINKED_LOCAL_SONG,
    MANUAL_USER_MARKED_MISSING,
    MANUAL_USER_MARKED_POSSIBLE,
)
from app.shared.constants.comparison import ComparisonStatus


class InMemoryYoutubePlaylistRepository(YoutubePlaylistRepository):
    def __init__(self) -> None:
        self._playlists: list[YoutubePlaylist] = []
        self._next_id = 1

    def get_active(self) -> YoutubePlaylist | None:
        for playlist in self._playlists:
            if playlist.is_active:
                return playlist
        return None

    def list_all(self) -> list[YoutubePlaylist]:
        return list(self._playlists)

    def save_as_active(
        self,
        playlist_url: str,
        external_playlist_id: str,
        title: str,
    ) -> YoutubePlaylist:
        self._playlists = [
            YoutubePlaylist(
                id=playlist.id,
                playlist_url=playlist.playlist_url,
                external_playlist_id=playlist.external_playlist_id,
                title=playlist.title,
                is_active=False,
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
            )
            for playlist in self._playlists
        ]

        for index, playlist in enumerate(self._playlists):
            if playlist.external_playlist_id != external_playlist_id:
                continue

            updated_playlist = YoutubePlaylist(
                id=playlist.id,
                playlist_url=playlist_url,
                external_playlist_id=external_playlist_id,
                title=title,
                is_active=True,
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
            )
            self._playlists[index] = updated_playlist
            return updated_playlist

        youtube_playlist = YoutubePlaylist(
            id=self._next_id,
            playlist_url=playlist_url,
            external_playlist_id=external_playlist_id,
            title=title,
            is_active=True,
        )
        self._playlists.append(youtube_playlist)
        self._next_id += 1
        return youtube_playlist

    def activate(self, youtube_playlist_id: int) -> YoutubePlaylist:
        self._playlists = [
            YoutubePlaylist(
                id=playlist.id,
                playlist_url=playlist.playlist_url,
                external_playlist_id=playlist.external_playlist_id,
                title=playlist.title,
                is_active=False,
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
            )
            for playlist in self._playlists
        ]

        for index, playlist in enumerate(self._playlists):
            if playlist.id != youtube_playlist_id:
                continue

            updated_playlist = YoutubePlaylist(
                id=playlist.id,
                playlist_url=playlist.playlist_url,
                external_playlist_id=playlist.external_playlist_id,
                title=playlist.title,
                is_active=True,
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
            )
            self._playlists[index] = updated_playlist
            return updated_playlist

        msg = "La playlist seleccionada no existe."
        raise ValueError(msg)

    def update(
        self,
        youtube_playlist_id: int,
        playlist_url: str,
        external_playlist_id: str,
        title: str,
    ) -> YoutubePlaylist:
        for existing_playlist in self._playlists:
            if (
                existing_playlist.external_playlist_id == external_playlist_id
                and existing_playlist.id != youtube_playlist_id
            ):
                msg = "Ya existe una playlist guardada con ese identificador de YouTube."
                raise ValueError(msg)
            if (
                existing_playlist.playlist_url == playlist_url
                and existing_playlist.id != youtube_playlist_id
            ):
                msg = "Ya existe una playlist guardada con esa URL."
                raise ValueError(msg)

        for index, playlist in enumerate(self._playlists):
            if playlist.id != youtube_playlist_id:
                continue

            updated_playlist = YoutubePlaylist(
                id=playlist.id,
                playlist_url=playlist_url,
                external_playlist_id=external_playlist_id,
                title=title,
                is_active=playlist.is_active,
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
            )
            self._playlists[index] = updated_playlist
            return updated_playlist

        msg = "La playlist seleccionada no existe."
        raise ValueError(msg)

    def delete(self, youtube_playlist_id: int) -> None:
        previous_count = len(self._playlists)
        self._playlists = [
            playlist for playlist in self._playlists if playlist.id != youtube_playlist_id
        ]
        if len(self._playlists) == previous_count:
            msg = "La playlist seleccionada no existe."
            raise ValueError(msg)


class InMemoryYoutubePlaylistItemRepository(YoutubePlaylistItemRepository):
    def __init__(self) -> None:
        self.items_by_playlist_id: dict[int, list[YoutubePlaylistItem]] = {}
        self.replace_calls: list[tuple[int, list[YoutubePlaylistItem]]] = []
        self.delete_calls: list[int] = []

    def count_by_playlist(self, youtube_playlist_id: int) -> int:
        return len(self.items_by_playlist_id.get(youtube_playlist_id, []))

    def list_by_playlist(self, youtube_playlist_id: int) -> list[YoutubePlaylistItem]:
        return list(self.items_by_playlist_id.get(youtube_playlist_id, []))

    def replace_for_playlist(
        self,
        youtube_playlist_id: int,
        items: list[YoutubePlaylistItem],
    ) -> list[YoutubePlaylistItem]:
        self.replace_calls.append((youtube_playlist_id, list(items)))
        persisted_items: list[YoutubePlaylistItem] = []
        for index, item in enumerate(items, start=1):
            persisted_items.append(
                YoutubePlaylistItem(
                    id=index,
                    youtube_playlist_id=item.youtube_playlist_id,
                    external_video_id=item.external_video_id,
                    position=item.position,
                    raw_title=item.raw_title,
                    raw_channel_name=item.raw_channel_name,
                    normalized_title=item.normalized_title,
                    normalized_artist=item.normalized_artist,
                    duration_seconds=item.duration_seconds,
                    published_at=item.published_at,
                )
            )
        self.items_by_playlist_id[youtube_playlist_id] = persisted_items
        return list(persisted_items)

    def delete_by_playlist(self, youtube_playlist_id: int) -> None:
        self.delete_calls.append(youtube_playlist_id)
        self.items_by_playlist_id.pop(youtube_playlist_id, None)


class InMemoryPlaylistComparisonRepository(PlaylistComparisonRepository):
    def __init__(self) -> None:
        self.created_comparisons: list[PlaylistComparison] = []
        self._next_id = 1
        self.commit_calls = 0

    def create(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> PlaylistComparison:
        comparison = PlaylistComparison(
            id=self._next_id,
            youtube_playlist_id=youtube_playlist_id,
            local_folder_id=local_folder_id,
        )
        self.created_comparisons.append(comparison)
        self._next_id += 1
        return comparison

    def find_by_id(
        self,
        playlist_comparison_id: int,
    ) -> PlaylistComparison | None:
        for comparison in self.created_comparisons:
            if comparison.id == playlist_comparison_id:
                return comparison
        return None

    def find_latest_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
    ) -> PlaylistComparison | None:
        for comparison in reversed(self.created_comparisons):
            if (
                comparison.youtube_playlist_id == youtube_playlist_id
                and comparison.local_folder_id == local_folder_id
            ):
                return comparison
        return None

    def list_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        limit: int,
    ) -> list[PlaylistComparison]:
        matching_comparisons = [
            comparison
            for comparison in self.created_comparisons
            if (
                comparison.youtube_playlist_id == youtube_playlist_id
                and comparison.local_folder_id == local_folder_id
            )
        ]
        ordered_comparisons = sorted(
            matching_comparisons,
            key=lambda comparison: (
                comparison.compared_at or datetime.min.replace(tzinfo=UTC),
                comparison.id or 0,
            ),
            reverse=True,
        )
        return ordered_comparisons[:limit]

    def list_excess_for_scope(
        self,
        youtube_playlist_id: int,
        local_folder_id: int,
        *,
        keep_latest: int,
    ) -> list[PlaylistComparison]:
        matching_comparisons = self.list_for_scope(
            youtube_playlist_id,
            local_folder_id,
            limit=10_000,
        )
        return matching_comparisons[keep_latest:]

    def delete_by_ids(
        self,
        playlist_comparison_ids: list[int],
    ) -> None:
        comparison_ids = set(playlist_comparison_ids)
        self.created_comparisons = [
            comparison
            for comparison in self.created_comparisons
            if comparison.id not in comparison_ids
        ]

    def commit(self) -> None:
        self.commit_calls += 1


class InMemoryPlaylistComparisonResultRepository(PlaylistComparisonResultRepository):
    def __init__(self) -> None:
        self.saved_results_by_comparison_id: dict[int, list[PlaylistComparisonResult]] = {}

    def find_by_comparison_item(
        self,
        playlist_comparison_id: int,
        youtube_playlist_item_id: int,
    ) -> PlaylistComparisonResult | None:
        for result in self.saved_results_by_comparison_id.get(playlist_comparison_id, []):
            if result.youtube_playlist_item_id == youtube_playlist_item_id:
                return result
        return None

    def save_for_comparison(
        self,
        playlist_comparison_id: int,
        results: list[PlaylistComparisonResult],
    ) -> list[PlaylistComparisonResult]:
        persisted_results: list[PlaylistComparisonResult] = []
        for index, result in enumerate(results, start=1):
            persisted_results.append(
                PlaylistComparisonResult(
                    id=index,
                    playlist_comparison_id=playlist_comparison_id,
                    youtube_playlist_item_id=result.youtube_playlist_item_id,
                    local_song_id=result.local_song_id,
                    match_status=result.match_status,
                    score=result.score,
                    matched_by=result.matched_by,
                )
            )
        self.saved_results_by_comparison_id[playlist_comparison_id] = persisted_results
        return list(persisted_results)

    def list_by_comparison(
        self,
        playlist_comparison_id: int,
    ) -> list[PlaylistComparisonResult]:
        return list(self.saved_results_by_comparison_id.get(playlist_comparison_id, []))

    def delete_by_comparison_id(
        self,
        playlist_comparison_id: int,
    ) -> None:
        self.saved_results_by_comparison_id.pop(playlist_comparison_id, None)

    def update_match_decision(
        self,
        *,
        playlist_comparison_id: int,
        youtube_playlist_item_id: int,
        match_status: str,
        local_song_id: int | None,
        matched_by: str,
    ) -> PlaylistComparisonResult:
        comparison_results = self.saved_results_by_comparison_id.get(
            playlist_comparison_id,
            [],
        )
        updated_results: list[PlaylistComparisonResult] = []
        persisted_result: PlaylistComparisonResult | None = None
        for existing_result in comparison_results:
            if existing_result.youtube_playlist_item_id != youtube_playlist_item_id:
                updated_results.append(existing_result)
                continue
            persisted_result = PlaylistComparisonResult(
                id=existing_result.id,
                playlist_comparison_id=existing_result.playlist_comparison_id,
                youtube_playlist_item_id=existing_result.youtube_playlist_item_id,
                local_song_id=local_song_id,
                match_status=match_status,
                score=existing_result.score,
                matched_by=matched_by,
                created_at=existing_result.created_at,
                updated_at=existing_result.updated_at,
            )
            updated_results.append(persisted_result)

        if persisted_result is None:
            raise ValueError("El resultado de comparacion seleccionado no existe.")
        self.saved_results_by_comparison_id[playlist_comparison_id] = updated_results
        return persisted_result


class YoutubePlaylistItemsImporterSpy:
    def __init__(
        self,
        items: list[ImportedYoutubePlaylistItemDto] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.items = items or []
        self.error = error
        self.received_playlist_url: str | None = None
        self.received_external_playlist_id: str | None = None

    def importItems(
        self,
        *,
        playlist_url: str,
        external_playlist_id: str,
    ) -> list[ImportedYoutubePlaylistItemDto]:
        self.received_playlist_url = playlist_url
        self.received_external_playlist_id = external_playlist_id
        if self.error is not None:
            raise self.error
        return list(self.items)


class LocalSongRepositorySpy(LocalSongRepository):
    def __init__(self, songs_by_folder_id: dict[int, list[LocalSong]] | None = None) -> None:
        self.songs_by_folder_id = songs_by_folder_id or {}
        self.list_by_folder_calls: list[int] = []

    def get_by_id(self, local_song_id: int):
        for songs in self.songs_by_folder_id.values():
            for song in songs:
                if song.id == local_song_id:
                    return song
        return None

    def list_by_folder(self, local_folder_id: int):
        self.list_by_folder_calls.append(local_folder_id)
        return list(self.songs_by_folder_id.get(local_folder_id, []))

    def get_by_file_path(self, file_path: str):
        return None

    def save(self, local_song):
        return local_song


class InMemoryLocalFolderRepository(LocalFolderRepository):
    def __init__(self, active_folder: LocalFolder | None = None) -> None:
        self._active_folder = active_folder

    def get_active(self) -> LocalFolder | None:
        return self._active_folder

    def save_as_active(self, path: str, display_name: str) -> LocalFolder:
        self._active_folder = LocalFolder(
            id=1,
            path=path,
            display_name=display_name,
            is_active=True,
        )
        return self._active_folder

    def list_all(self) -> list[LocalFolder]:
        return [self._active_folder] if self._active_folder is not None else []

    def activate(self, local_folder_id: int) -> LocalFolder:
        if self._active_folder is None or self._active_folder.id != local_folder_id:
            raise ValueError("La biblioteca seleccionada no existe.")
        return self._active_folder

    def update(self, local_folder_id: int, path: str, display_name: str) -> LocalFolder:
        if self._active_folder is None or self._active_folder.id != local_folder_id:
            raise ValueError("La biblioteca seleccionada no existe.")
        self._active_folder = LocalFolder(
            id=local_folder_id,
            path=path,
            display_name=display_name,
            is_active=self._active_folder.is_active,
        )
        return self._active_folder

    def delete(self, local_folder_id: int) -> None:
        if self._active_folder is None or self._active_folder.id != local_folder_id:
            raise ValueError("La biblioteca seleccionada no existe.")
        self._active_folder = None


class InMemoryIgnoredTermRepository(IgnoredTermRepository):
    def __init__(self, terms: list[IgnoredTerm] | None = None) -> None:
        self._terms = list(terms or [])

    def list_all(self):
        return list(self._terms)

    def create(self, term: str, scope: str, language: str) -> IgnoredTerm:
        ignored_term = IgnoredTerm(
            id=len(self._terms) + 1,
            term=term,
            scope=scope,
            language=language,
            is_active=True,
        )
        self._terms.append(ignored_term)
        return ignored_term

    def update(self, term_id: int, term: str, scope: str, language: str) -> IgnoredTerm:
        for index, ignored_term in enumerate(self._terms):
            if ignored_term.id != term_id:
                continue
            updated_term = IgnoredTerm(
                id=ignored_term.id,
                term=term,
                scope=scope,
                language=language,
                is_active=ignored_term.is_active,
                created_at=ignored_term.created_at,
                updated_at=ignored_term.updated_at,
            )
            self._terms[index] = updated_term
            return updated_term
        raise ValueError("El termino ignorado seleccionado no existe.")

    def delete(self, term_id: int) -> None:
        self._terms = [ignored_term for ignored_term in self._terms if ignored_term.id != term_id]


def test_define_main_youtube_playlist_use_case_persists_playlist_as_active() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    youtube_playlist = use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="  https://www.youtube.com/playlist?list=PL1234567890  ",
            title="  Favoritas junio  ",
        )
    )

    assert youtube_playlist.playlist_url == "https://www.youtube.com/playlist?list=PL1234567890"
    assert youtube_playlist.external_playlist_id == "PL1234567890"
    assert youtube_playlist.title == "Favoritas junio"
    assert youtube_playlist.is_active is True


def test_define_main_youtube_playlist_use_case_rejects_non_youtube_url() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    with pytest.raises(ValueError, match="no pertenece a YouTube"):
        use_case.execute(
            DefineMainYoutubePlaylistInputDto(
                playlist_url="https://open.spotify.com/playlist/123",
                title="Mi playlist",
            )
        )


def test_define_main_youtube_playlist_use_case_rejects_empty_title() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    with pytest.raises(ValueError, match="nombre de la playlist"):
        use_case.execute(
            DefineMainYoutubePlaylistInputDto(
                playlist_url="https://www.youtube.com/playlist?list=PL123",
                title="   ",
            )
        )


def test_define_main_youtube_playlist_use_case_rejects_url_without_list_parameter() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    with pytest.raises(ValueError, match="parametro list"):
        use_case.execute(
            DefineMainYoutubePlaylistInputDto(
                playlist_url="https://www.youtube.com/watch?v=abc123",
                title="Mi playlist",
            )
        )


def test_get_active_youtube_playlist_use_case_returns_none_when_no_playlist_is_active() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = GetActiveYoutubePlaylistUseCase(
        repository,
        InMemoryYoutubePlaylistItemRepository(),
    )

    assert use_case.execute() is None


def test_list_youtube_playlists_use_case_returns_saved_playlists() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    define_use_case = DefineMainYoutubePlaylistUseCase(repository)
    item_repository = InMemoryYoutubePlaylistItemRepository()
    list_use_case = ListYoutubePlaylistsUseCase(repository, item_repository)

    define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLFIRST",
            title="Lista uno",
        )
    )
    define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://music.youtube.com/playlist?list=PLSECOND",
            title="Lista dos",
        )
    )

    youtube_playlists = list_use_case.execute()

    assert len(youtube_playlists) == 2
    assert {youtube_playlist.external_playlist_id for youtube_playlist in youtube_playlists} == {
        "PLFIRST",
        "PLSECOND",
    }


def test_list_youtube_playlists_use_case_includes_item_count_for_each_playlist() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    item_repository = InMemoryYoutubePlaylistItemRepository()
    first_playlist = repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PLFIRST",
        external_playlist_id="PLFIRST",
        title="Lista uno",
    )
    second_playlist = repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PLSECOND",
        external_playlist_id="PLSECOND",
        title="Lista dos",
    )
    item_repository.items_by_playlist_id[first_playlist.id or 0] = [
        YoutubePlaylistItem(
            id=1,
            youtube_playlist_id=first_playlist.id or 0,
            external_video_id="one",
            position=1,
            raw_title="Song One",
            raw_channel_name="Artist One",
            normalized_title="song one",
            normalized_artist="artist one",
        )
    ]
    item_repository.items_by_playlist_id[second_playlist.id or 0] = [
        YoutubePlaylistItem(
            id=2,
            youtube_playlist_id=second_playlist.id or 0,
            external_video_id="two",
            position=1,
            raw_title="Song Two",
            raw_channel_name="Artist Two",
            normalized_title="song two",
            normalized_artist="artist two",
        ),
        YoutubePlaylistItem(
            id=3,
            youtube_playlist_id=second_playlist.id or 0,
            external_video_id="three",
            position=2,
            raw_title="Song Three",
            raw_channel_name="Artist Three",
            normalized_title="song three",
            normalized_artist="artist three",
        ),
    ]
    use_case = ListYoutubePlaylistsUseCase(repository, item_repository)

    youtube_playlists = use_case.execute()

    assert [youtube_playlist.item_count for youtube_playlist in youtube_playlists] == [1, 2]


def test_activate_youtube_playlist_use_case_switches_active_playlist() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    define_use_case = DefineMainYoutubePlaylistUseCase(repository)
    activate_use_case = ActivateYoutubePlaylistUseCase(repository)

    first_playlist = define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLFIRST",
            title="Lista uno",
        )
    )
    define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLSECOND",
            title="Lista dos",
        )
    )

    activated_playlist = activate_use_case.execute(
        ActivateYoutubePlaylistInputDto(youtube_playlist_id=first_playlist.id)
    )

    assert activated_playlist.id == first_playlist.id
    assert activated_playlist.is_active is True
    active_playlist = repository.get_active()
    assert active_playlist is not None
    assert active_playlist.id == first_playlist.id


def test_update_youtube_playlist_use_case_updates_selected_playlist() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    define_use_case = DefineMainYoutubePlaylistUseCase(repository)
    update_use_case = UpdateYoutubePlaylistUseCase(repository)

    created_playlist = define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLFIRST",
            title="Lista uno",
        )
    )

    updated_playlist = update_use_case.execute(
        UpdateYoutubePlaylistInputDto(
            youtube_playlist_id=created_playlist.id,
            playlist_url="https://www.youtube.com/playlist?list=PLUPDATED",
            title="Lista actualizada",
        )
    )

    assert updated_playlist.external_playlist_id == "PLUPDATED"
    assert updated_playlist.title == "Lista actualizada"


def test_delete_youtube_playlist_use_case_removes_selected_playlist() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    define_use_case = DefineMainYoutubePlaylistUseCase(repository)
    delete_use_case = DeleteYoutubePlaylistUseCase(repository)

    created_playlist = define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLFIRST",
            title="Lista uno",
        )
    )

    delete_use_case.execute(
        DeleteYoutubePlaylistInputDto(youtube_playlist_id=created_playlist.id)
    )

    assert repository.list_all() == []


def test_import_youtube_playlist_items_use_case_fails_when_no_playlist_is_active() -> None:
    use_case = ImportYoutubePlaylistItemsUseCase(
        InMemoryYoutubePlaylistRepository(),
        InMemoryYoutubePlaylistItemRepository(),
        YoutubePlaylistItemsImporterSpy(),
    )

    with pytest.raises(ValueError, match="playlist principal activa"):
        use_case.execute()


def test_import_youtube_playlist_items_use_case_imports_and_replaces_snapshot() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="old-item",
                position=1,
                raw_title="Old Song",
                raw_channel_name="Old Artist",
                normalized_title="old song",
                normalized_artist="old artist",
            )
        ],
    )
    importer = YoutubePlaylistItemsImporterSpy(
        items=[
            ImportedYoutubePlaylistItemDto(
                external_video_id="abc123",
                position=1,
                raw_title="Kendrick Lamar - HUMBLE. (Official Video)",
                raw_channel_name="KendrickLamarVEVO",
                duration_seconds=177.0,
            ),
            ImportedYoutubePlaylistItemDto(
                external_video_id="def456",
                position=2,
                raw_title="DNA. [Lyrics]",
                raw_channel_name="Kendrick Lamar",
                duration_seconds=185.0,
            ),
        ]
    )
    use_case = ImportYoutubePlaylistItemsUseCase(
        playlist_repository,
        item_repository,
        importer,
    )

    result = use_case.execute()
    persisted_items = item_repository.list_by_playlist(active_playlist.id or 0)

    assert importer.received_playlist_url == "https://www.youtube.com/playlist?list=PL123"
    assert importer.received_external_playlist_id == "PL123"
    assert result.youtube_playlist_id == active_playlist.id
    assert result.playlist_title == "Favoritas"
    assert result.imported_item_count == 2
    assert result.created_item_count == 2
    assert result.updated_item_count == 0
    assert result.existing_item_count == 0
    assert result.removed_item_count == 1
    assert len(persisted_items) == 2
    assert persisted_items[0].external_video_id == "abc123"
    assert persisted_items[0].normalized_artist == "kendrick lamar"
    assert persisted_items[0].normalized_title == "humble"
    assert persisted_items[1].external_video_id == "def456"
    assert persisted_items[1].normalized_artist == "kendrick lamar"
    assert persisted_items[1].normalized_title == "dna"


def test_import_youtube_playlist_items_use_case_replaces_previous_snapshot() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.items_by_playlist_id[active_playlist.id or 0] = [
        YoutubePlaylistItem(
            id=1,
            youtube_playlist_id=active_playlist.id or 0,
            external_video_id="obsolete",
            position=1,
            raw_title="Obsolete Song",
            raw_channel_name="Obsolete Artist",
            normalized_title="obsolete song",
            normalized_artist="obsolete artist",
        )
    ]
    importer = YoutubePlaylistItemsImporterSpy(
        items=[
            ImportedYoutubePlaylistItemDto(
                external_video_id="fresh",
                position=1,
                raw_title="Fresh Song",
                raw_channel_name="Fresh Artist",
            )
        ]
    )
    use_case = ImportYoutubePlaylistItemsUseCase(
        playlist_repository,
        item_repository,
        importer,
    )

    use_case.execute()
    persisted_items = item_repository.list_by_playlist(active_playlist.id or 0)

    assert [item.external_video_id for item in persisted_items] == ["fresh"]
    assert len(item_repository.replace_calls) == 1


def test_import_youtube_playlist_items_use_case_detects_updated_and_unchanged_items() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.items_by_playlist_id[active_playlist.id or 0] = [
        YoutubePlaylistItem(
            id=1,
            youtube_playlist_id=active_playlist.id or 0,
            external_video_id="stable",
            position=1,
            raw_title="Stable Song",
            raw_channel_name="Stable Artist",
            normalized_title="stable song",
            normalized_artist="stable artist",
            duration_seconds=180.0,
        ),
        YoutubePlaylistItem(
            id=2,
            youtube_playlist_id=active_playlist.id or 0,
            external_video_id="moved",
            position=2,
            raw_title="Moved Song",
            raw_channel_name="Moved Artist",
            normalized_title="moved song",
            normalized_artist="moved artist",
            duration_seconds=200.0,
        ),
    ]
    importer = YoutubePlaylistItemsImporterSpy(
        items=[
            ImportedYoutubePlaylistItemDto(
                external_video_id="stable",
                position=1,
                raw_title="Stable Song",
                raw_channel_name="Stable Artist",
                duration_seconds=180.0,
            ),
            ImportedYoutubePlaylistItemDto(
                external_video_id="moved",
                position=5,
                raw_title="Moved Song",
                raw_channel_name="Moved Artist",
                duration_seconds=200.0,
            ),
        ]
    )
    use_case = ImportYoutubePlaylistItemsUseCase(
        playlist_repository,
        item_repository,
        importer,
    )

    result = use_case.execute()

    assert result.imported_item_count == 2
    assert result.created_item_count == 0
    assert result.updated_item_count == 1
    assert result.existing_item_count == 1
    assert result.removed_item_count == 0


def test_import_youtube_playlist_items_use_case_propagates_importer_errors() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    importer = YoutubePlaylistItemsImporterSpy(
        error=YoutubePlaylistImportExtractorError("Extractor exploded")
    )
    use_case = ImportYoutubePlaylistItemsUseCase(
        playlist_repository,
        InMemoryYoutubePlaylistItemRepository(),
        importer,
    )

    with pytest.raises(YoutubePlaylistImportExtractorError, match="Extractor exploded"):
        use_case.execute()


def test_list_active_youtube_playlist_items_use_case_returns_empty_when_no_playlist_is_active() -> None:
    use_case = ListActiveYoutubePlaylistItemsUseCase(
        InMemoryYoutubePlaylistRepository(),
        InMemoryYoutubePlaylistItemRepository(),
    )

    assert use_case.execute() == []


def test_list_active_youtube_playlist_items_use_case_returns_snapshot_with_comparable_fields() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="abc123",
                position=1,
                raw_title="Kendrick Lamar - HUMBLE. (Official Video)",
                raw_channel_name="KendrickLamarVEVO",
                normalized_title="humble.",
                normalized_artist="kendrick lamar",
                duration_seconds=177.0,
            )
        ],
    )
    use_case = ListActiveYoutubePlaylistItemsUseCase(
        playlist_repository,
        item_repository,
    )

    youtube_playlist_items = use_case.execute()

    assert len(youtube_playlist_items) == 1
    assert youtube_playlist_items[0].youtube_playlist_id == active_playlist.id
    assert youtube_playlist_items[0].normalized_title == "humble."
    assert youtube_playlist_items[0].normalized_artist == "kendrick lamar"
    assert youtube_playlist_items[0].duration_seconds == 177.0


def test_compare_youtube_playlist_with_local_library_use_case_requires_active_playlist() -> None:
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        InMemoryYoutubePlaylistRepository(),
        InMemoryYoutubePlaylistItemRepository(),
        InMemoryLocalFolderRepository(),
        LocalSongRepositorySpy(),
        InMemoryPlaylistComparisonRepository(),
        InMemoryPlaylistComparisonResultRepository(),
    )

    with pytest.raises(ValueError, match="playlist principal activa"):
        use_case.execute()


def test_compare_youtube_playlist_with_local_library_use_case_requires_active_local_folder() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="abc123",
                position=1,
                raw_title="Song",
                raw_channel_name="Artist",
                normalized_title="song",
                normalized_artist="artist",
                duration_seconds=180.0,
            )
        ],
    )
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(),
        LocalSongRepositorySpy(),
        InMemoryPlaylistComparisonRepository(),
        InMemoryPlaylistComparisonResultRepository(),
    )

    with pytest.raises(ValueError, match="biblioteca local activa"):
        use_case.execute()


def test_compare_youtube_playlist_with_local_library_use_case_returns_summary_and_detail_with_mixed_statuses() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
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
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=11,
                    local_folder_id=active_folder.id,
                    file_name="song-one.mp3",
                    is_available=True,
                    title="Song One",
                    artist="Artist One",
                    duration_seconds=181.0,
                ),
                LocalSong(
                    id=12,
                    local_folder_id=active_folder.id,
                    file_name="song-two-live.mp3",
                    is_available=True,
                    title="Song Two Live",
                    artist="Artist Two Remix",
                    duration_seconds=200.0,
                ),
                LocalSong(
                    id=13,
                    local_folder_id=active_folder.id,
                    file_name="hidden.mp3",
                    is_available=False,
                    title="Missing Song",
                    artist="Missing Artist",
                    duration_seconds=240.0,
                ),
            ]
        }
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    result = use_case.execute()

    assert isinstance(result, PlaylistComparisonResultDto)
    assert local_song_repository.list_by_folder_calls == [7]
    assert result.summary.found_count == 1
    assert result.summary.possible_match_count == 0
    assert result.summary.missing_count == 2
    assert result.summary.total_compared == 3
    assert result.last_compared_at is not None
    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.FOUND,
        ComparisonStatus.MISSING,
        ComparisonStatus.MISSING,
    ]
    assert result.items[0].local_song_id == 11
    assert result.items[1].local_song_id is None
    assert result.items[2].local_song_id is None
    assert len(comparison_repository.created_comparisons) == 1
    persisted_results = comparison_result_repository.saved_results_by_comparison_id[1]
    assert [item.score for item in persisted_results] == [
        result.items[0].score,
        result.items[1].score,
        result.items[2].score,
    ]
    assert [item.match_status for item in persisted_results] == [
        ComparisonStatus.FOUND.value,
        ComparisonStatus.MISSING.value,
        ComparisonStatus.MISSING.value,
    ]
    assert [item.matched_by for item in persisted_results] == [
        AUTO_TITLE_ARTIST_DURATION,
        AUTO_NO_COMPETITIVE_CANDIDATE,
        AUTO_NO_COMPETITIVE_CANDIDATE,
    ]


def test_compare_youtube_playlist_with_local_library_use_case_keeps_folele_present_when_exists_in_local() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="folele-item",
                position=1,
                raw_title="Cruz Cafuné - Folelé ft. BOJ (Visualizer)",
                raw_channel_name="Cruz Cafuné",
                normalized_title="cruz cafune folele ft boj visualizer",
                normalized_artist="cruz cafune folele ft boj visualizer",
                duration_seconds=227.8,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=21,
                    local_folder_id=active_folder.id,
                    file_name="folele.mp3",
                    is_available=True,
                    title="Folelé",
                    artist="Cruz Cafuné",
                    duration_seconds=227.8,
                )
            ]
        }
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    result = use_case.execute()

    assert result.summary.found_count == 1
    assert result.summary.missing_count == 0
    assert result.last_compared_at is not None
    assert result.items[0].comparison_status is ComparisonStatus.FOUND
    assert result.items[0].local_song_id == 21
    assert result.items[0].reason == "Titulo exacto con artista fuerte y duracion razonable."


def test_compare_youtube_playlist_with_local_library_use_case_applies_persisted_ignored_terms_to_playlist_and_local() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="deluxe-item",
                position=1,
                raw_title="Artist One - Song One Deluxe",
                raw_channel_name="Artist One",
                normalized_title="artist one song one deluxe",
                normalized_artist="artist one",
                duration_seconds=180.0,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=31,
                    local_folder_id=active_folder.id,
                    file_name="song-one-deluxe.mp3",
                    is_available=True,
                    title="Song One Deluxe",
                    artist="Artist One",
                    duration_seconds=180.6,
                )
            ]
        }
    )
    ignored_term_repository = InMemoryIgnoredTermRepository(
        [
            IgnoredTerm(
                id=1,
                term="deluxe",
                scope="title",
                language="global",
                is_active=True,
            )
        ]
    )
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        InMemoryPlaylistComparisonRepository(),
        InMemoryPlaylistComparisonResultRepository(),
        ignored_term_repository,
    )

    result = use_case.execute()

    assert result.summary.found_count == 1
    assert result.summary.missing_count == 0
    assert result.items[0].comparison_status is ComparisonStatus.FOUND
    assert result.items[0].local_song_id == 31


def test_compare_youtube_playlist_with_local_library_use_case_retains_only_three_snapshots_per_scope() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
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
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=11,
                    local_folder_id=active_folder.id,
                    file_name="song-one.mp3",
                    is_available=True,
                    title="Song One",
                    artist="Artist One",
                    duration_seconds=181.0,
                )
            ]
        }
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    other_scope = comparison_repository.create(active_playlist.id or 0, 8)
    comparison_result_repository.save_for_comparison(
        other_scope.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=other_scope.id or 0,
                youtube_playlist_item_id=99,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
            )
        ],
    )
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    for _ in range(4):
        use_case.execute()

    retained_scope_ids = [
        comparison.id
        for comparison in comparison_repository.list_for_scope(
            active_playlist.id or 0,
            active_folder.id or 0,
            limit=10,
        )
    ]

    assert retained_scope_ids == [5, 4, 3]
    assert comparison_result_repository.list_by_comparison(2) == []
    assert comparison_result_repository.list_by_comparison(3) != []
    assert comparison_result_repository.list_by_comparison(other_scope.id or 0) != []
    assert comparison_repository.commit_calls == 4


def test_compare_youtube_playlist_with_local_library_use_case_keeps_new_snapshot_and_limits_history_to_three() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    item_repository.replace_for_playlist(
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
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=11,
                    local_folder_id=active_folder.id,
                    file_name="song-one.mp3",
                    is_available=True,
                    title="Song One",
                    artist="Artist One",
                    duration_seconds=181.0,
                )
            ]
        }
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    latest_result = None
    for _ in range(4):
        latest_result = use_case.execute()

    if latest_result is None:
        raise AssertionError("Se esperaba el DTO de la ultima comparacion.")

    comparison_repository.created_comparisons = [
        PlaylistComparison(
            id=comparison.id,
            youtube_playlist_id=comparison.youtube_playlist_id,
            local_folder_id=comparison.local_folder_id,
            compared_at=datetime(2026, 6, 8, 8, 0, tzinfo=UTC)
            if comparison.id == 2
            else datetime(2026, 6, 8, 9, 0, tzinfo=UTC)
            if comparison.id == 3
            else datetime(2026, 6, 8, 10, 0, tzinfo=UTC)
            if comparison.id == 4
            else comparison.compared_at,
            created_at=comparison.created_at,
        )
        for comparison in comparison_repository.created_comparisons
    ]

    latest_comparison = comparison_repository.find_latest_for_scope(
        active_playlist.id or 0,
        active_folder.id or 0,
    )
    history = ListPersistedPlaylistComparisonHistoryUseCase(
        playlist_repository,
        InMemoryLocalFolderRepository(active_folder),
        comparison_repository,
        comparison_result_repository,
    ).execute(limit=5)
    persisted_snapshot = LoadPersistedPlaylistComparisonUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    ).execute()

    assert latest_comparison is not None
    assert latest_comparison.id == 4
    assert latest_result.last_compared_at is not None
    assert comparison_result_repository.list_by_comparison(latest_comparison.id or 0) != []
    assert len(comparison_result_repository.list_by_comparison(latest_comparison.id or 0)) == 1
    assert len(history) == 3
    assert [entry.comparison_id for entry in history] == [4, 3, 2]
    assert persisted_snapshot is not None
    _local_songs, comparison_result = persisted_snapshot
    assert comparison_result.last_compared_at == latest_comparison.compared_at
    assert comparison_result.items[0].comparison_status is ComparisonStatus.FOUND


def test_compare_youtube_playlist_with_local_library_use_case_propagates_repository_errors() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )

    class BrokenLocalSongRepository(LocalSongRepository):
        def get_by_id(self, local_song_id: int):
            return None

        def list_by_folder(self, local_folder_id: int):
            raise RuntimeError("DB exploded")

        def get_by_file_path(self, file_path: str):
            return None

        def save(self, local_song):
            return local_song

    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        InMemoryYoutubePlaylistItemRepository(),
        InMemoryLocalFolderRepository(active_folder),
        BrokenLocalSongRepository(),
        InMemoryPlaylistComparisonRepository(),
        InMemoryPlaylistComparisonResultRepository(),
    )

    with pytest.raises(RuntimeError, match="DB exploded"):
        use_case.execute()


def test_load_persisted_playlist_comparison_use_case_returns_none_without_snapshot() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    use_case = LoadPersistedPlaylistComparisonUseCase(
        playlist_repository,
        InMemoryYoutubePlaylistItemRepository(),
        InMemoryLocalFolderRepository(active_folder),
        LocalSongRepositorySpy(),
        InMemoryPlaylistComparisonRepository(),
        InMemoryPlaylistComparisonResultRepository(),
    )

    assert use_case.execute() is None


def test_load_persisted_playlist_comparison_use_case_rehydrates_last_snapshot_for_active_scope() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    persisted_items = item_repository.replace_for_playlist(
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
                raw_title="Missing Song",
                raw_channel_name="Missing Artist",
                normalized_title="missing song",
                normalized_artist="missing artist",
                duration_seconds=200.0,
            ),
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=11,
                    local_folder_id=active_folder.id,
                    file_path=r"C:\Music\Active\song-one.mp3",
                    file_name="song-one.mp3",
                    is_available=True,
                    title="Song One",
                    artist="Artist One",
                    album="Album One",
                    release_year=2024,
                    track_number_album=1,
                    duration_seconds=181.0,
                )
            ]
        }
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(active_playlist.id or 0, active_folder.id or 0)
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    comparison_result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=persisted_items[0].id or 0,
                local_song_id=11,
                match_status=ComparisonStatus.FOUND.value,
                score=100.0,
                matched_by="Titulo exacto con artista fuerte y duracion razonable.",
            ),
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=persisted_items[1].id or 0,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by="Duracion fuera de tolerancia fuerte.",
            ),
        ],
    )
    use_case = LoadPersistedPlaylistComparisonUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    persisted_snapshot = use_case.execute()

    assert persisted_snapshot is not None
    local_songs, comparison_result = persisted_snapshot
    assert local_song_repository.list_by_folder_calls == [7]
    assert [song.id for song in local_songs] == [11]
    assert comparison_result.last_compared_at == comparison.compared_at
    assert comparison_result.summary.found_count == 1
    assert comparison_result.summary.missing_count == 1
    assert comparison_result.summary.possible_match_count == 0
    assert comparison_result.summary.total_compared == 2
    assert comparison_result.items[0].youtube_title == "Song One"
    assert comparison_result.items[0].local_title == "Song One"
    assert comparison_result.items[0].score == 100.0
    assert (
        comparison_result.items[0].reason
        == "Titulo exacto con artista fuerte y duracion razonable."
    )
    assert comparison_result.items[1].comparison_status is ComparisonStatus.MISSING
    assert comparison_result.items[1].local_song_id is None
    assert comparison_result.items[1].reason == "Duracion fuera de tolerancia fuerte."


def test_load_persisted_playlist_comparison_use_case_rehydrates_manual_override_reason_and_link() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    persisted_items = item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="manual-item",
                position=1,
                raw_title="Manual Song",
                raw_channel_name="Youtube Artist",
                normalized_title="manual song",
                normalized_artist="youtube artist",
                duration_seconds=180.0,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            active_folder.id or 0: [
                LocalSong(
                    id=11,
                    local_folder_id=active_folder.id,
                    file_path=r"C:\Music\Active\manual-song.mp3",
                    file_name="manual-song.mp3",
                    is_available=True,
                    title="Manual Song Local",
                    artist="Manual Artist",
                    album="Album One",
                    release_year=2024,
                    track_number_album=1,
                    duration_seconds=180.0,
                )
            ]
        }
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(active_playlist.id or 0, active_folder.id or 0)
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    comparison_result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=persisted_items[0].id or 0,
                local_song_id=11,
                match_status=ComparisonStatus.FOUND.value,
                score=0.0,
                matched_by=MANUAL_USER_LINKED_LOCAL_SONG,
            )
        ],
    )
    use_case = LoadPersistedPlaylistComparisonUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    persisted_snapshot = use_case.execute()

    assert persisted_snapshot is not None
    _, comparison_result = persisted_snapshot
    assert comparison_result.items[0].comparison_status is ComparisonStatus.FOUND
    assert comparison_result.items[0].local_song_id == 11
    assert comparison_result.items[0].local_title == "Manual Song Local"
    assert comparison_result.items[0].local_artist == "Manual Artist"
    assert comparison_result.items[0].matched_by == MANUAL_USER_LINKED_LOCAL_SONG
    assert (
        comparison_result.items[0].reason
        == "Enlace manual con cancion local decidido por el usuario."
    )


def test_load_persisted_playlist_comparison_use_case_keeps_manual_link_when_song_is_not_selectable() -> None:
    class LocalSongRepositoryWithHiddenLinkedSong(LocalSongRepositorySpy):
        def __init__(self) -> None:
            super().__init__(
                songs_by_folder_id={
                    7: [
                        LocalSong(
                            id=11,
                            local_folder_id=7,
                            file_path=r"C:\Music\Active\visible-song.mp3",
                            file_name="visible-song.mp3",
                            is_available=True,
                            title="Visible Song",
                            artist="Visible Artist",
                            duration_seconds=180.0,
                        )
                    ]
                }
            )
            self.hidden_linked_song = LocalSong(
                id=99,
                local_folder_id=7,
                file_path=r"C:\Music\Active\hidden-manual-link.mp3",
                file_name="hidden-manual-link.mp3",
                is_available=False,
                title="Hidden Manual Song",
                artist="Hidden Artist",
                duration_seconds=181.0,
            )

        def get_by_id(self, local_song_id: int):
            if local_song_id == self.hidden_linked_song.id:
                return self.hidden_linked_song
            return super().get_by_id(local_song_id)

    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    item_repository = InMemoryYoutubePlaylistItemRepository()
    persisted_items = item_repository.replace_for_playlist(
        active_playlist.id or 0,
        [
            YoutubePlaylistItem(
                id=None,
                youtube_playlist_id=active_playlist.id or 0,
                external_video_id="manual-hidden-item",
                position=1,
                raw_title="Hidden Manual Song",
                raw_channel_name="Youtube Artist",
                normalized_title="hidden manual song",
                normalized_artist="youtube artist",
                duration_seconds=181.0,
            )
        ],
    )
    local_song_repository = LocalSongRepositoryWithHiddenLinkedSong()
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(active_playlist.id or 0, active_folder.id or 0)
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()
    comparison_result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=persisted_items[0].id or 0,
                local_song_id=99,
                match_status=ComparisonStatus.FOUND.value,
                score=0.0,
                matched_by=MANUAL_USER_LINKED_LOCAL_SONG,
            )
        ],
    )
    use_case = LoadPersistedPlaylistComparisonUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
        comparison_repository,
        comparison_result_repository,
    )

    persisted_snapshot = use_case.execute()

    assert persisted_snapshot is not None
    local_songs, comparison_result = persisted_snapshot
    assert [song.id for song in local_songs] == [11]
    assert comparison_result.items[0].local_song_id == 99
    assert comparison_result.items[0].local_title == "Hidden Manual Song"
    assert comparison_result.items[0].local_artist == "Hidden Artist"


def test_list_persisted_playlist_comparison_history_use_case_returns_recent_runs_for_active_scope() -> None:
    playlist_repository = InMemoryYoutubePlaylistRepository()
    active_playlist = playlist_repository.save_as_active(
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        title="Favoritas",
    )
    active_folder = LocalFolder(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison_result_repository = InMemoryPlaylistComparisonResultRepository()

    first_comparison = comparison_repository.create(active_playlist.id or 0, active_folder.id or 0)
    comparison_repository.created_comparisons[0] = PlaylistComparison(
        id=first_comparison.id,
        youtube_playlist_id=first_comparison.youtube_playlist_id,
        local_folder_id=first_comparison.local_folder_id,
        compared_at=datetime(2026, 6, 8, 8, 0, tzinfo=UTC),
    )
    comparison_result_repository.save_for_comparison(
        first_comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=first_comparison.id or 0,
                youtube_playlist_item_id=1,
                local_song_id=10,
                match_status=ComparisonStatus.FOUND.value,
                score=100.0,
                matched_by=None,
            )
        ],
    )

    second_comparison = comparison_repository.create(active_playlist.id or 0, active_folder.id or 0)
    comparison_repository.created_comparisons[1] = PlaylistComparison(
        id=second_comparison.id,
        youtube_playlist_id=second_comparison.youtube_playlist_id,
        local_folder_id=second_comparison.local_folder_id,
        compared_at=datetime(2026, 6, 8, 9, 0, tzinfo=UTC),
    )
    comparison_result_repository.save_for_comparison(
        second_comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=second_comparison.id or 0,
                youtube_playlist_item_id=2,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by=None,
            ),
            PlaylistComparisonResult(
                playlist_comparison_id=second_comparison.id or 0,
                youtube_playlist_item_id=3,
                local_song_id=11,
                match_status=ComparisonStatus.POSSIBLE_MATCH.value,
                score=72.0,
                matched_by=None,
            ),
        ],
    )

    use_case = ListPersistedPlaylistComparisonHistoryUseCase(
        playlist_repository,
        InMemoryLocalFolderRepository(active_folder),
        comparison_repository,
        comparison_result_repository,
    )

    history = use_case.execute(limit=5)

    assert history == [
        PlaylistComparisonHistoryEntryDto(
            comparison_id=second_comparison.id or 0,
            compared_at=datetime(2026, 6, 8, 9, 0, tzinfo=UTC),
            found_count=0,
            missing_count=1,
            possible_match_count=1,
            total_compared=2,
        ),
        PlaylistComparisonHistoryEntryDto(
            comparison_id=first_comparison.id or 0,
            compared_at=datetime(2026, 6, 8, 8, 0, tzinfo=UTC),
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        ),
    ]


def test_in_memory_playlist_comparison_repositories_support_scope_retention_operations() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    result_repository = InMemoryPlaylistComparisonResultRepository()

    first = comparison_repository.create(9, 7)
    second = comparison_repository.create(9, 7)
    third = comparison_repository.create(9, 7)
    fourth = comparison_repository.create(9, 7)
    other_scope = comparison_repository.create(9, 8)

    result_repository.save_for_comparison(
        first.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=first.id or 0,
                youtube_playlist_item_id=1,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
            )
        ],
    )

    excess = comparison_repository.list_excess_for_scope(9, 7, keep_latest=3)

    assert [comparison.id for comparison in excess] == [first.id]

    result_repository.delete_by_comparison_id(first.id or 0)
    comparison_repository.delete_by_ids([first.id or 0])

    assert result_repository.list_by_comparison(first.id or 0) == []
    assert [comparison.id for comparison in comparison_repository.created_comparisons] == [
        second.id,
        third.id,
        fourth.id,
        other_scope.id,
    ]


def test_in_memory_playlist_comparison_repositories_keep_other_playlist_and_other_folder_scopes() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    result_repository = InMemoryPlaylistComparisonResultRepository()

    same_scope_first = comparison_repository.create(9, 7)
    same_scope_second = comparison_repository.create(9, 7)
    same_scope_third = comparison_repository.create(9, 7)
    same_scope_fourth = comparison_repository.create(9, 7)
    same_playlist_other_folder = comparison_repository.create(9, 8)
    other_playlist_same_folder = comparison_repository.create(10, 7)

    for comparison in comparison_repository.created_comparisons:
        result_repository.save_for_comparison(
            comparison.id or 0,
            [
                PlaylistComparisonResult(
                    playlist_comparison_id=comparison.id or 0,
                    youtube_playlist_item_id=(comparison.id or 0) * 10,
                    local_song_id=None,
                    match_status=ComparisonStatus.MISSING.value,
                    score=0.0,
                )
            ],
        )

    excess = comparison_repository.list_excess_for_scope(9, 7, keep_latest=3)
    excess_ids = [comparison.id for comparison in excess if comparison.id is not None]
    for comparison_id in excess_ids:
        result_repository.delete_by_comparison_id(comparison_id)
    comparison_repository.delete_by_ids(excess_ids)

    retained_same_scope = comparison_repository.list_for_scope(9, 7, limit=10)
    assert [comparison.id for comparison in retained_same_scope] == [
        same_scope_fourth.id,
        same_scope_third.id,
        same_scope_second.id,
    ]
    assert comparison_repository.find_latest_for_scope(9, 7) == retained_same_scope[0]
    assert result_repository.list_by_comparison(same_scope_first.id or 0) == []
    assert result_repository.list_by_comparison(same_scope_fourth.id or 0) != []
    assert comparison_repository.find_latest_for_scope(9, 8) == same_playlist_other_folder
    assert comparison_repository.find_latest_for_scope(10, 7) == other_playlist_same_folder
    assert result_repository.list_by_comparison(same_playlist_other_folder.id or 0) != []
    assert result_repository.list_by_comparison(other_playlist_same_folder.id or 0) != []


def test_update_playlist_comparison_result_use_case_updates_single_row_with_manual_link() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(9, 7)
    result_repository = InMemoryPlaylistComparisonResultRepository()
    result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=55.0,
                matched_by=AUTO_NO_COMPETITIVE_CANDIDATE,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            7: [
                LocalSong(
                    id=99,
                    local_folder_id=7,
                    file_path=r"C:\Music\Active\song.mp3",
                    file_name="song.mp3",
                    is_available=True,
                    title="Song",
                    artist="Artist",
                    duration_seconds=180.0,
                )
            ]
        }
    )
    use_case = UpdatePlaylistComparisonResultUseCase(
        comparison_repository,
        result_repository,
        local_song_repository,
    )

    updated_result = use_case.execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=comparison.id or 0,
            youtube_playlist_item_id=21,
            match_status=ComparisonStatus.FOUND.value,
            local_song_id=99,
        )
    )

    assert updated_result.local_song_id == 99
    assert updated_result.match_status == ComparisonStatus.FOUND.value
    assert updated_result.score == 55.0
    assert updated_result.matched_by == MANUAL_USER_LINKED_LOCAL_SONG
    assert comparison_repository.commit_calls == 1


def test_update_playlist_comparison_result_use_case_rejects_local_song_from_other_folder() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(9, 7)
    result_repository = InMemoryPlaylistComparisonResultRepository()
    result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=55.0,
                matched_by=AUTO_NO_COMPETITIVE_CANDIDATE,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            8: [
                LocalSong(
                    id=99,
                    local_folder_id=8,
                    file_path=r"C:\Music\Other\song.mp3",
                    file_name="song.mp3",
                    is_available=True,
                    title="Song",
                    artist="Artist",
                    duration_seconds=180.0,
                )
            ]
        }
    )
    use_case = UpdatePlaylistComparisonResultUseCase(
        comparison_repository,
        result_repository,
        local_song_repository,
    )

    with pytest.raises(ValueError, match="biblioteca del snapshot"):
        use_case.execute(
            UpdatePlaylistComparisonResultInputDto(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                match_status=ComparisonStatus.FOUND.value,
                local_song_id=99,
            )
        )


def test_update_playlist_comparison_result_use_case_marks_possible_without_replacing_score() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(9, 7)
    result_repository = InMemoryPlaylistComparisonResultRepository()
    result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                local_song_id=11,
                match_status=ComparisonStatus.FOUND.value,
                score=91.0,
                matched_by=AUTO_TITLE_ARTIST_DURATION,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            7: [
                LocalSong(
                    id=11,
                    local_folder_id=7,
                    file_path=r"C:\Music\Active\song.mp3",
                    file_name="song.mp3",
                    is_available=True,
                    title="Song",
                    artist="Artist",
                    duration_seconds=180.0,
                )
            ]
        }
    )
    use_case = UpdatePlaylistComparisonResultUseCase(
        comparison_repository,
        result_repository,
        local_song_repository,
    )

    updated_result = use_case.execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=comparison.id or 0,
            youtube_playlist_item_id=21,
            match_status=ComparisonStatus.POSSIBLE_MATCH.value,
            local_song_id=11,
        )
    )

    assert updated_result.local_song_id == 11
    assert updated_result.match_status == ComparisonStatus.POSSIBLE_MATCH.value
    assert updated_result.score == 91.0
    assert updated_result.matched_by == MANUAL_USER_MARKED_POSSIBLE


def test_update_playlist_comparison_result_use_case_marks_missing_and_clears_link() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(9, 7)
    result_repository = InMemoryPlaylistComparisonResultRepository()
    result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                local_song_id=11,
                match_status=ComparisonStatus.FOUND.value,
                score=91.0,
                matched_by=AUTO_TITLE_ARTIST_DURATION,
            )
        ],
    )
    local_song_repository = LocalSongRepositorySpy(
        songs_by_folder_id={
            7: [
                LocalSong(
                    id=11,
                    local_folder_id=7,
                    file_path=r"C:\Music\Active\song.mp3",
                    file_name="song.mp3",
                    is_available=True,
                    title="Song",
                    artist="Artist",
                    duration_seconds=180.0,
                )
            ]
        }
    )
    use_case = UpdatePlaylistComparisonResultUseCase(
        comparison_repository,
        result_repository,
        local_song_repository,
    )

    updated_result = use_case.execute(
        UpdatePlaylistComparisonResultInputDto(
            playlist_comparison_id=comparison.id or 0,
            youtube_playlist_item_id=21,
            match_status=ComparisonStatus.MISSING.value,
            local_song_id=11,
        )
    )

    assert updated_result.local_song_id is None
    assert updated_result.match_status == ComparisonStatus.MISSING.value
    assert updated_result.score == 91.0
    assert updated_result.matched_by == MANUAL_USER_MARKED_MISSING


def test_update_playlist_comparison_result_use_case_rejects_found_without_local_song() -> None:
    comparison_repository = InMemoryPlaylistComparisonRepository()
    comparison = comparison_repository.create(9, 7)
    result_repository = InMemoryPlaylistComparisonResultRepository()
    result_repository.save_for_comparison(
        comparison.id or 0,
        [
            PlaylistComparisonResult(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                local_song_id=None,
                match_status=ComparisonStatus.MISSING.value,
                score=0.0,
                matched_by=AUTO_NO_COMPETITIVE_CANDIDATE,
            )
        ],
    )
    use_case = UpdatePlaylistComparisonResultUseCase(
        comparison_repository,
        result_repository,
        LocalSongRepositorySpy(),
    )

    with pytest.raises(ValueError, match="debes seleccionar una cancion local"):
        use_case.execute(
            UpdatePlaylistComparisonResultInputDto(
                playlist_comparison_id=comparison.id or 0,
                youtube_playlist_item_id=21,
                match_status=ComparisonStatus.FOUND.value,
                local_song_id=None,
            )
        )
