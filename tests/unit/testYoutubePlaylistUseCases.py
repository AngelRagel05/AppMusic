from __future__ import annotations

import pytest

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
    ListActiveYoutubePlaylistItemsUseCase,
    ListYoutubePlaylistsUseCase,
    UpdateYoutubePlaylistUseCase,
)
from app.application.use_cases.playlists.youtubePlaylistItemsImporterPort import (
    YoutubePlaylistImportExtractorError,
)
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.playlists.entities.youtubePlaylist import YoutubePlaylist
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.domain.library.repositories.localSongRepository import LocalSongRepository
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
    assert persisted_items[0].normalized_title == "humble."
    assert persisted_items[1].external_video_id == "def456"
    assert persisted_items[1].normalized_artist == "kendrick lamar"
    assert persisted_items[1].normalized_title == "dna."


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
    use_case = CompareYoutubePlaylistWithLocalLibraryUseCase(
        playlist_repository,
        item_repository,
        InMemoryLocalFolderRepository(active_folder),
        local_song_repository,
    )

    result = use_case.execute()

    assert isinstance(result, PlaylistComparisonResultDto)
    assert local_song_repository.list_by_folder_calls == [7]
    assert result.summary.found_count == 1
    assert result.summary.possible_match_count == 1
    assert result.summary.missing_count == 1
    assert result.summary.total_compared == 3
    assert [item.comparison_status for item in result.items] == [
        ComparisonStatus.FOUND,
        ComparisonStatus.POSSIBLE_MATCH,
        ComparisonStatus.MISSING,
    ]
    assert result.items[0].local_song_id == 11
    assert result.items[1].local_song_id == 12
    assert result.items[2].local_song_id is None


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
    )

    with pytest.raises(RuntimeError, match="DB exploded"):
        use_case.execute()
