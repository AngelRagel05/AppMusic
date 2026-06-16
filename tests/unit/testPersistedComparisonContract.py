from __future__ import annotations

from app.application.dto.importedYoutubePlaylistItemDto import ImportedYoutubePlaylistItemDto
from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.use_cases.library.scanLocalFolderUseCase import ScanLocalFolderUseCase
from app.application.use_cases.playlists.importYoutubePlaylistItemsUseCase import (
    ImportYoutubePlaylistItemsUseCase,
)
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong
from app.domain.playlists.entities.youtubePlaylist import YoutubePlaylist
from app.domain.playlists.entities.youtubePlaylistItem import YoutubePlaylistItem
from app.domain.playlists.services import (
    ComparisonDependenciesFingerprint,
    ComparisonRefreshAction,
    ComparisonRefreshRequest,
    matchPersistedPlaylistItemToLocalSongs,
    resolveComparisonRefreshAction,
    shouldInvalidatePersistedFoundMatch,
)
import app.domain.playlists.services.youtubePlaylistItemNormalizationService as youtubePlaylistItemNormalizationService
import app.domain.metadata.services.musicComparisonNormalizationService as musicComparisonNormalizationService


class ActiveLocalFolderRepositoryStub:
    def __init__(self, active_folder: LocalFolder) -> None:
        self._active_folder = active_folder

    def get_active(self) -> LocalFolder | None:
        return self._active_folder


class SavingLocalSongRepositorySpy:
    def __init__(self) -> None:
        self.saved_songs: list[LocalSong] = []

    def list_by_folder(self, _local_folder_id: int) -> list[LocalSong]:
        return []

    def save(self, local_song: LocalSong) -> LocalSong:
        self.saved_songs.append(local_song)
        return local_song


class LocalMusicScannerStub:
    def __init__(self, file_paths: list[str]) -> None:
        self._file_paths = file_paths

    def scanMp3Files(self, _folder_path: str) -> list[str]:
        return list(self._file_paths)


class LocalSongMetadataReaderStub:
    def __init__(self, metadata_by_path: dict[str, LocalSongMetadataDto]) -> None:
        self._metadata_by_path = metadata_by_path

    def readMetadata(self, filePath: str) -> LocalSongMetadataDto:
        return self._metadata_by_path[filePath]


class ActiveYoutubePlaylistRepositoryStub:
    def __init__(self, active_playlist: YoutubePlaylist) -> None:
        self._active_playlist = active_playlist

    def get_active(self) -> YoutubePlaylist | None:
        return self._active_playlist


class YoutubePlaylistItemRepositorySpy:
    def __init__(self) -> None:
        self.persisted_items: list[YoutubePlaylistItem] = []

    def list_by_playlist(self, _youtube_playlist_id: int) -> list[YoutubePlaylistItem]:
        return []

    def replace_for_playlist(
        self,
        _youtube_playlist_id: int,
        items: list[YoutubePlaylistItem],
    ) -> list[YoutubePlaylistItem]:
        self.persisted_items = list(items)
        return list(items)


class YoutubePlaylistItemsImporterStub:
    def __init__(self, items: list[ImportedYoutubePlaylistItemDto]) -> None:
        self._items = items

    def importItems(
        self,
        *,
        playlist_url: str,
        external_playlist_id: str,
    ) -> list[ImportedYoutubePlaylistItemDto]:
        del playlist_url
        del external_playlist_id
        return list(self._items)


def test_scan_local_folder_use_case_persists_comparable_local_values() -> None:
    file_path = r"C:\Music\Active\memories-i.mp3"
    repository = SavingLocalSongRepositorySpy()
    use_case = ScanLocalFolderUseCase(
        ActiveLocalFolderRepositoryStub(
            LocalFolder(
                id=7,
                path=r"C:\Music\Active",
                display_name="Active",
                is_active=True,
            )
        ),
        repository,
        LocalMusicScannerStub([file_path]),
        LocalSongMetadataReaderStub(
            {
                file_path: LocalSongMetadataDto(
                    title="memories i",
                    artist="nadal015",
                    album="ep uno",
                    release_year=2026,
                    track_number_album=1,
                    duration_seconds=175.8,
                )
            }
        ),
    )

    result = use_case.execute()

    assert result.scanned_file_count == 1
    persisted_song = repository.saved_songs[0]
    assert persisted_song.title == "memories i"
    assert persisted_song.artist == "nadal015"


def test_import_youtube_playlist_items_use_case_persists_normalized_youtube_values() -> None:
    repository = YoutubePlaylistItemRepositorySpy()
    use_case = ImportYoutubePlaylistItemsUseCase(
        ActiveYoutubePlaylistRepositoryStub(
            YoutubePlaylist(
                id=9,
                playlist_url="https://www.youtube.com/playlist?list=PL123",
                external_playlist_id="PL123",
                title="Favoritas",
                is_active=True,
            )
        ),
        repository,
        YoutubePlaylistItemsImporterStub(
            [
                ImportedYoutubePlaylistItemDto(
                    external_video_id="abc123",
                    position=1,
                    raw_title="CRUZ CAFUNÉ - Practice ft. HOKE (Visualizer)",
                    raw_channel_name="Cruz Cafuné",
                    duration_seconds=228.0,
                )
            ]
        ),
    )

    result = use_case.execute()

    assert result.imported_item_count == 1
    persisted_item = repository.persisted_items[0]
    assert persisted_item.normalized_title == "practice"
    assert persisted_item.normalized_artist == "cruz cafune"


def test_resolve_comparison_refresh_action_separates_view_refresh_from_recompare() -> None:
    assert (
        resolveComparisonRefreshAction(ComparisonRefreshRequest.REFRESH_VIEW)
        is ComparisonRefreshAction.LOAD_PERSISTED_SNAPSHOT
    )
    assert (
        resolveComparisonRefreshAction(ComparisonRefreshRequest.RECOMPARE)
        is ComparisonRefreshAction.RECOMPUTE_COMPARISON
    )


def test_should_invalidate_persisted_found_match_when_any_dependency_changes() -> None:
    persisted = ComparisonDependenciesFingerprint(
        youtube_playlist_version="yt-v1",
        local_library_version="local-v1",
        ignored_terms_version="ignored-v1",
        matching_rules_version="rules-v1",
    )
    current = ComparisonDependenciesFingerprint(
        youtube_playlist_version="yt-v2",
        local_library_version="local-v1",
        ignored_terms_version="ignored-v1",
        matching_rules_version="rules-v1",
    )

    assert (
        shouldInvalidatePersistedFoundMatch(
            persisted_dependencies=persisted,
            current_dependencies=current,
            local_song_is_available=True,
        )
        is True
    )


def test_should_invalidate_persisted_found_match_when_linked_song_is_unavailable() -> None:
    dependencies = ComparisonDependenciesFingerprint(
        youtube_playlist_version="yt-v1",
        local_library_version="local-v1",
        ignored_terms_version="ignored-v1",
        matching_rules_version="rules-v1",
    )

    assert (
        shouldInvalidatePersistedFoundMatch(
            persisted_dependencies=dependencies,
            current_dependencies=dependencies,
            local_song_is_available=False,
        )
        is True
    )


def test_should_keep_persisted_found_match_when_dependencies_stay_equal_and_song_is_available() -> None:
    dependencies = ComparisonDependenciesFingerprint(
        youtube_playlist_version="yt-v1",
        local_library_version="local-v1",
        ignored_terms_version="ignored-v1",
        matching_rules_version="rules-v1",
    )

    assert (
        shouldInvalidatePersistedFoundMatch(
            persisted_dependencies=dependencies,
            current_dependencies=dependencies,
            local_song_is_available=True,
        )
        is False
    )


def test_match_persisted_playlist_item_to_local_songs_uses_only_persisted_comparable_fields(
    monkeypatch,
) -> None:
    def failYoutubeNormalization(*args, **kwargs):
        raise AssertionError("La comparacion persistida no debe normalizar YouTube.")

    def failLocalNormalization(*args, **kwargs):
        raise AssertionError("La comparacion persistida no debe normalizar local.")

    monkeypatch.setattr(
        youtubePlaylistItemNormalizationService,
        "normalizeYoutubePlaylistItemMetadata",
        failYoutubeNormalization,
    )
    monkeypatch.setattr(
        musicComparisonNormalizationService,
        "normalizeMusicComparisonMetadata",
        failLocalNormalization,
    )

    result = matchPersistedPlaylistItemToLocalSongs(
        YoutubePlaylistItem(
            id=21,
            youtube_playlist_id=9,
            external_video_id="abc123",
            position=1,
            raw_title="NADAL 015  #MEMORIES I",
            raw_channel_name="NADAL 015",
            normalized_title="memories i",
            normalized_artist="nadal015",
            duration_seconds=176.0,
        ),
        [
            LocalSong(
                id=77,
                file_name="Nadal015 - Memories I.mp3",
                title="memories i",
                artist="nadal015",
                duration_seconds=175.8,
            )
        ],
    )

    assert result.comparison_status.value == "found"
    assert result.local_song is not None
    assert result.local_song.id == 77
