from __future__ import annotations

from datetime import UTC, datetime

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonHistoryEntryDto import (
    PlaylistComparisonHistoryEntryDto,
)
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.features.comparison.controller.comparisonController import (
    ComparisonController,
)
from app.presentation.features.ignoredTerms.controller.ignoredTermsController import (
    IgnoredTermsController,
)
from app.presentation.features.localLibrary.controller.localLibraryController import (
    LocalLibraryController,
)
from app.presentation.viewmodels.localLibrary.localLibraryScanViewModel import (
    LocalLibraryScanFeedback,
)
from app.presentation.viewmodels.comparison.libraryComparisonViewModel import (
    LibraryComparisonFeedback,
)
from app.presentation.viewmodels.youtubePlaylists.youtubePlaylistImportViewModel import (
    YoutubePlaylistImportFeedback,
)
from app.presentation.features.youtubePlaylists.controller.youtubePlaylistsController import (
    YoutubePlaylistsController,
)
from app.shared.constants.comparison import ComparisonStatus


class PageCallbackPort:
    def __init__(self) -> None:
        self.callback = None

    def connect(self, callback) -> None:
        self.callback = callback


class LocalLibraryPageSpy:
    def __init__(self) -> None:
        self.primaryActionRequested = PageCallbackPort()
        self.secondaryActionRequested = PageCallbackPort()
        self.browseRequested = PageCallbackPort()
        self.saveRequested = PageCallbackPort()
        self.activateRequested = PageCallbackPort()
        self.editRequested = PageCallbackPort()
        self.deleteRequested = PageCallbackPort()
        self.folder_path = ""
        self.folder_display_name = ""
        self.save_mode = None
        self.status_messages: list[tuple[str, str]] = []
        self.after_calls: list[int] = []

    def onPrimaryActionRequested(self, callback) -> None:
        self.primaryActionRequested.connect(callback)

    def onSecondaryActionRequested(self, callback) -> None:
        self.secondaryActionRequested.connect(callback)

    def onBrowseFolderRequested(self, callback) -> None:
        self.browseRequested.connect(callback)

    def onSaveFolderRequested(self, callback) -> None:
        self.saveRequested.connect(callback)

    def onActivateFolderRequested(self, callback) -> None:
        self.activateRequested.connect(callback)

    def onEditFolderRequested(self, callback) -> None:
        self.editRequested.connect(callback)

    def onDeleteFolderRequested(self, callback) -> None:
        self.deleteRequested.connect(callback)

    def showFolders(self, _localFolders) -> None:
        return None

    def showActiveFolder(self, _activeFolder) -> None:
        return None

    def folderPath(self) -> str:
        return self.folder_path

    def setFolderPath(self, path: str) -> None:
        self.folder_path = path

    def folderDisplayName(self) -> str:
        return self.folder_display_name

    def setFolderDisplayName(self, display_name: str) -> None:
        self.folder_display_name = display_name

    def setSaveMode(self, isEditing: bool) -> None:
        self.save_mode = isEditing

    def clearForm(self) -> None:
        self.folder_path = ""
        self.folder_display_name = ""

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.status_messages.append((message, tone))

    def focusPrimaryInput(self) -> None:
        return None

    def after(self, delay_ms: int, callback) -> None:
        self.after_calls.append(delay_ms)
        callback()


class LocalLibraryViewModelSpy:
    def __init__(self, selected_folder: LocalFolderDto | None) -> None:
        self.selected_folder = selected_folder
        self.find_calls: list[int] = []
        self.activate_calls: list[int] = []
        self.update_calls: list[tuple[int, str, str]] = []

    def refreshState(self):
        if self.selected_folder is None:
            return [], None
        active_folder = self.selected_folder if self.selected_folder.is_active else None
        return [self.selected_folder], active_folder

    def load_folders(self):
        if self.selected_folder is None:
            return []
        return [self.selected_folder]

    def load_active_folder(self):
        return self.selected_folder if self.selected_folder and self.selected_folder.is_active else None

    def find_folder_by_id(self, local_folder_id: int):
        self.find_calls.append(local_folder_id)
        return self.selected_folder

    def activate_folder(self, local_folder_id: int):
        self.activate_calls.append(local_folder_id)
        return self.selected_folder

    def update_folder(self, local_folder_id: int, path: str, display_name: str):
        self.update_calls.append((local_folder_id, path, display_name))
        return self.selected_folder

    def delete_folder(self, _local_folder_id: int) -> None:
        return None


class LocalLibraryScanViewModelSpy:
    def __init__(self, feedbacks: list[LocalLibraryScanFeedback] | None = None) -> None:
        self.feedbacks = feedbacks or []
        self.received_active_folder = None
        self.request_calls = 0

    def requestScan(
        self,
        active_folder,
        schedule_on_main_thread,
        on_feedback,
        automatic: bool = False,
    ) -> None:
        self.request_calls += 1
        self.received_active_folder = active_folder
        for feedback in self.feedbacks:
            on_feedback(feedback)


class LocalFolderMonitorWorkerSpy:
    def __init__(self) -> None:
        self.watch_calls: list[str | None] = []
        self.stop_calls = 0
        self.on_folder_changed = None
        self.on_failed = None

    def watch(self, folder_path, on_folder_changed, on_failed) -> None:
        self.watch_calls.append(folder_path)
        self.on_folder_changed = on_folder_changed
        self.on_failed = on_failed

    def stop(self) -> None:
        self.stop_calls += 1


class IgnoredTermsPageSpy:
    def __init__(self) -> None:
        self.saveRequested = PageCallbackPort()
        self.editRequested = PageCallbackPort()
        self.deleteRequested = PageCallbackPort()
        self.term_text = ""
        self.term_scope = ""
        self.term_language = ""
        self.save_mode = None
        self.status_messages: list[tuple[str, str]] = []

    def onSaveTermRequested(self, callback) -> None:
        self.saveRequested.connect(callback)

    def onEditTermRequested(self, callback) -> None:
        self.editRequested.connect(callback)

    def onDeleteTermRequested(self, callback) -> None:
        self.deleteRequested.connect(callback)

    def showTerms(self, _ignoredTerms) -> None:
        return None

    def termText(self) -> str:
        return self.term_text

    def termScope(self) -> str:
        return self.term_scope

    def termLanguage(self) -> str:
        return self.term_language

    def clearTermInput(self) -> None:
        self.term_text = ""

    def setTermText(self, value: str) -> None:
        self.term_text = value

    def setTermScope(self, value: str) -> None:
        self.term_scope = value

    def setTermLanguage(self, value: str) -> None:
        self.term_language = value

    def setSaveMode(self, isEditing: bool) -> None:
        self.save_mode = isEditing

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.status_messages.append((message, tone))

    def focusPrimaryInput(self) -> None:
        return None


class IgnoredTermsViewModelSpy:
    def __init__(self, selected_term: IgnoredTermDto | None) -> None:
        self.selected_term = selected_term
        self.find_calls: list[int] = []

    def refreshState(self):
        return []

    def load_terms(self):
        raise AssertionError("load_terms no debe usarse para buscar por id")

    def find_term_by_id(self, term_id: int):
        self.find_calls.append(term_id)
        return self.selected_term


class YoutubePlaylistsPageSpy:
    def __init__(self) -> None:
        self.primaryActionRequested = PageCallbackPort()
        self.saveRequested = PageCallbackPort()
        self.activateRequested = PageCallbackPort()
        self.editRequested = PageCallbackPort()
        self.deleteRequested = PageCallbackPort()
        self.playlist_title = ""
        self.playlist_url = ""
        self.save_mode = None
        self.status_messages: list[tuple[str, str]] = []
        self.after_calls: list[int] = []

    def onPrimaryActionRequested(self, callback) -> None:
        self.primaryActionRequested.connect(callback)

    def onSavePlaylistRequested(self, callback) -> None:
        self.saveRequested.connect(callback)

    def onActivatePlaylistRequested(self, callback) -> None:
        self.activateRequested.connect(callback)

    def onEditPlaylistRequested(self, callback) -> None:
        self.editRequested.connect(callback)

    def onDeletePlaylistRequested(self, callback) -> None:
        self.deleteRequested.connect(callback)

    def showPlaylists(self, _playlists) -> None:
        return None

    def showActivePlaylist(self, _playlist) -> None:
        return None

    def playlistTitle(self) -> str:
        return self.playlist_title

    def playlistUrl(self) -> str:
        return self.playlist_url

    def setPlaylistTitle(self, value: str) -> None:
        self.playlist_title = value

    def setPlaylistUrl(self, value: str) -> None:
        self.playlist_url = value

    def setSaveMode(self, isEditing: bool) -> None:
        self.save_mode = isEditing

    def clearForm(self) -> None:
        self.playlist_title = ""
        self.playlist_url = ""

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.status_messages.append((message, tone))

    def focusPrimaryInput(self) -> None:
        return None

    def after(self, delay_ms: int, callback) -> None:
        self.after_calls.append(delay_ms)
        callback()


class YoutubePlaylistsViewModelSpy:
    def __init__(self, selected_playlist: YoutubePlaylistDto | None) -> None:
        self.selected_playlist = selected_playlist
        self.find_calls: list[int] = []
        self.activate_calls: list[int] = []

    def refreshState(self):
        if self.selected_playlist is None:
            return [], None
        active_playlist = self.selected_playlist if self.selected_playlist.is_active else None
        return [self.selected_playlist], active_playlist

    def load_playlists(self):
        raise AssertionError("load_playlists no debe usarse para buscar por id")

    def load_active_playlist(self):
        return self.selected_playlist if self.selected_playlist and self.selected_playlist.is_active else None

    def find_playlist_by_id(self, youtube_playlist_id: int):
        self.find_calls.append(youtube_playlist_id)
        return self.selected_playlist

    def activate_playlist(self, youtube_playlist_id: int):
        self.activate_calls.append(youtube_playlist_id)
        return self.selected_playlist


class YoutubePlaylistImportViewModelSpy:
    def __init__(
        self,
        feedbacks: list[YoutubePlaylistImportFeedback] | None = None,
    ) -> None:
        self.feedbacks = feedbacks or []
        self.request_calls = 0
        self.received_active_playlist = None

    def requestImport(
        self,
        active_playlist,
        schedule_on_main_thread,
        on_feedback,
    ) -> None:
        self.request_calls += 1
        self.received_active_playlist = active_playlist
        for feedback in self.feedbacks:
            on_feedback(feedback)


class ComparisonPageSpy:
    DEFAULT_PRIMARY_ACTION_LABEL = "↻ Refrescar"
    RERUN_PRIMARY_ACTION_LABEL = "↻ Volver a comparar"

    def __init__(self, *, confirms_comparison: bool = True) -> None:
        self.local_songs = None
        self.comparison_result = None
        self.comparison_history = None
        self.status_messages: list[tuple[str, str]] = []
        self.after_calls: list[int] = []
        self.loading_messages: list[str] = []
        self.loading_hidden = 0
        self.primary_action_callback = None
        self.confirms_comparison = confirms_comparison
        self.confirmation_requests = 0
        self.confirmation_payloads: list[tuple[str, str]] = []
        self.primary_action_labels: list[str] = []

    def showLocalSongs(self, local_songs) -> None:
        self.local_songs = local_songs

    def showComparisonData(self, local_songs, comparison_result) -> None:
        self.local_songs = local_songs
        self.comparison_result = comparison_result

    def onPrimaryActionRequested(self, callback) -> None:
        self.primary_action_callback = callback

    def confirmManualComparisonStart(self, *, playlist_title: str, folder_name: str) -> bool:
        self.confirmation_requests += 1
        self.confirmation_payloads.append((playlist_title, folder_name))
        return self.confirms_comparison

    def showComparisonResults(self, comparison_result) -> None:
        self.comparison_result = comparison_result

    def showComparisonHistory(self, comparison_history) -> None:
        self.comparison_history = comparison_history

    def showComparisonStatusMessage(self, message: str, tone: str = "info") -> None:
        self.status_messages.append((message, tone))

    def setPrimaryActionLabel(self, label: str) -> None:
        self.primary_action_labels.append(label)

    def showLoadingState(self, message: str) -> None:
        self.loading_messages.append(message)

    def hideLoadingState(self) -> None:
        self.loading_hidden += 1

    def after(self, delay_ms: int, callback) -> None:
        self.after_calls.append(delay_ms)
        callback()


class LibraryComparisonViewModelSpy:
    def __init__(
        self,
        feedbacks: list[LibraryComparisonFeedback] | None = None,
        *,
        cached_local_songs=None,
        cached_comparison_result=None,
        cached_comparison_history=None,
        persisted_local_songs=None,
        persisted_comparison_result=None,
        persisted_comparison_history=None,
        is_stale: bool = True,
    ) -> None:
        self.feedbacks = feedbacks or []
        self.request_calls = 0
        self.cached_local_songs = cached_local_songs or []
        self.cached_comparison_result = cached_comparison_result
        self.cached_comparison_history = cached_comparison_history or []
        self.persisted_local_songs = persisted_local_songs or []
        self.persisted_comparison_result = persisted_comparison_result
        self.persisted_comparison_history = persisted_comparison_history or []
        self.is_stale = is_stale
        self.invalidate_calls = 0
        self.restore_calls = 0

    def requestComparison(
        self,
        schedule_on_main_thread,
        on_feedback,
    ) -> None:
        self.request_calls += 1
        for feedback in self.feedbacks:
            on_feedback(feedback)

    def load_local_songs(self):
        return self.cached_local_songs

    def load_comparison_result(self):
        return self.cached_comparison_result

    def load_comparison_history(self):
        return self.cached_comparison_history

    def hasCachedComparison(self) -> bool:
        return self.cached_comparison_result is not None

    def restorePersistedComparison(self) -> bool:
        self.restore_calls += 1
        if self.persisted_comparison_result is None:
            return False
        self.cached_local_songs = list(self.persisted_local_songs)
        self.cached_comparison_result = self.persisted_comparison_result
        self.cached_comparison_history = list(self.persisted_comparison_history)
        self.is_stale = False
        return True

    def isComparisonStale(self) -> bool:
        return self.is_stale

    def invalidateComparison(self) -> None:
        self.invalidate_calls += 1
        self.is_stale = True


class ActiveComparisonContextSpy:
    def __init__(self, *, folder=None, playlist=None) -> None:
        self.folder = folder
        self.playlist = playlist

    def load_active_folder(self):
        return self.folder

    def load_active_playlist(self):
        return self.playlist


def test_local_library_controller_uses_view_model_lookup_for_editing_selected_folder() -> None:
    page = LocalLibraryPageSpy()
    selected_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=False,
    )
    view_model = LocalLibraryViewModelSpy(selected_folder)
    shown_pages: list[tuple[str, bool]] = []
    controller = LocalLibraryController(
        page=page,
        view_model=view_model,
        scan_view_model=LocalLibraryScanViewModelSpy(),
        folder_monitor_worker=LocalFolderMonitorWorkerSpy(),
        show_page=lambda page_name, focus_input: shown_pages.append((page_name, focus_input)),
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )

    controller._handleEditFolderById(7)

    assert view_model.find_calls == [7]
    assert page.folder_path == r"C:\Music\Jazz"
    assert page.folder_display_name == "Jazz"
    assert page.save_mode is True
    assert shown_pages == [("localLibrary", True)]
    assert page.status_messages[-1] == ('Editando la biblioteca "Jazz".', "info")


def test_local_library_controller_does_not_reactivate_active_folder() -> None:
    page = LocalLibraryPageSpy()
    active_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=True,
    )
    view_model = LocalLibraryViewModelSpy(active_folder)
    controller = LocalLibraryController(
        page=page,
        view_model=view_model,
        scan_view_model=LocalLibraryScanViewModelSpy(),
        folder_monitor_worker=LocalFolderMonitorWorkerSpy(),
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )

    controller._handleActivateFolderById(7)

    assert view_model.find_calls == [7]
    assert view_model.activate_calls == []
    assert page.status_messages[-1] == ('La biblioteca "Jazz" ya esta activa.', "info")


def test_local_library_controller_sends_visible_name_when_updating_folder() -> None:
    page = LocalLibraryPageSpy()
    page.folder_path = r"C:\Music\Jazz"
    page.folder_display_name = "Jazz personalizada"
    selected_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=False,
    )
    view_model = LocalLibraryViewModelSpy(selected_folder)
    controller = LocalLibraryController(
        page=page,
        view_model=view_model,
        scan_view_model=LocalLibraryScanViewModelSpy(),
        folder_monitor_worker=LocalFolderMonitorWorkerSpy(),
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )
    controller._editing_folder_id = 7

    controller._handleSaveFolder()

    assert view_model.update_calls == [(7, r"C:\Music\Jazz", "Jazz personalizada")]


def test_local_library_controller_delegates_scan_and_updates_song_count() -> None:
    page = LocalLibraryPageSpy()
    active_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=True,
    )
    view_model = LocalLibraryViewModelSpy(active_folder)
    scan_view_model = LocalLibraryScanViewModelSpy(
        feedbacks=[
            LocalLibraryScanFeedback(
                status_message='Escaneando la biblioteca "Jazz"...',
                status_tone="info",
                song_count_label="Escaneando...",
            ),
            LocalLibraryScanFeedback(
                status_message='Escaneo completado en "Jazz": 2 MP3 detectados, 1 anadidas, 1 actualizadas y 0 eliminadas.',
                status_tone="success",
                song_count_label="2 MP3 detectados",
                last_action_message='Escaneo completado en "Jazz": 2 MP3 detectados, 1 anadidas, 1 actualizadas y 0 eliminadas.',
            ),
        ]
    )
    folder_monitor_worker = LocalFolderMonitorWorkerSpy()
    song_count_updates: list[str] = []
    recorded_actions: list[str] = []
    controller = LocalLibraryController(
        page=page,
        view_model=view_model,
        scan_view_model=scan_view_model,
        folder_monitor_worker=folder_monitor_worker,
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: recorded_actions.append("invalidate"),
        on_action_recorded=recorded_actions.append,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=song_count_updates.append,
    )

    controller._handleScanLibraryRequested()

    assert scan_view_model.request_calls == 1
    assert scan_view_model.received_active_folder == active_folder
    assert song_count_updates == ["Escaneando...", "2 MP3 detectados"]
    assert "invalidate" in recorded_actions
    assert recorded_actions[-1] == 'Escaneo completado en "Jazz": 2 MP3 detectados, 1 anadidas, 1 actualizadas y 0 eliminadas.'
    assert page.status_messages[0] == ('Escaneando la biblioteca "Jazz"...', "info")
    assert page.status_messages[-1] == (
        'Escaneo completado en "Jazz": 2 MP3 detectados, 1 anadidas, 1 actualizadas y 0 eliminadas.',
        "success",
    )


def test_local_library_controller_registers_only_primary_scan_action() -> None:
    page = LocalLibraryPageSpy()
    controller = LocalLibraryController(
        page=page,
        view_model=LocalLibraryViewModelSpy(None),
        scan_view_model=LocalLibraryScanViewModelSpy(),
        folder_monitor_worker=LocalFolderMonitorWorkerSpy(),
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )

    controller.bindEvents()

    assert page.primaryActionRequested.callback is not None
    assert page.secondaryActionRequested.callback is None


def test_local_library_controller_starts_auto_refresh_for_active_folder_on_load() -> None:
    page = LocalLibraryPageSpy()
    active_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=True,
    )
    view_model = LocalLibraryViewModelSpy(active_folder)
    folder_monitor_worker = LocalFolderMonitorWorkerSpy()
    controller = LocalLibraryController(
        page=page,
        view_model=view_model,
        scan_view_model=LocalLibraryScanViewModelSpy(),
        folder_monitor_worker=folder_monitor_worker,
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )

    controller.load()

    assert folder_monitor_worker.watch_calls == [r"C:\Music\Jazz"]


def test_local_library_controller_triggers_scan_when_auto_refresh_detects_change() -> None:
    page = LocalLibraryPageSpy()
    active_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=True,
    )
    scan_view_model = LocalLibraryScanViewModelSpy()
    folder_monitor_worker = LocalFolderMonitorWorkerSpy()
    controller = LocalLibraryController(
        page=page,
        view_model=LocalLibraryViewModelSpy(active_folder),
        scan_view_model=scan_view_model,
        folder_monitor_worker=folder_monitor_worker,
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )
    controller.load()
    if folder_monitor_worker.on_folder_changed is None:
        raise AssertionError("Se esperaba callback de auto-refresh registrado.")

    folder_monitor_worker.on_folder_changed()

    assert scan_view_model.request_calls == 1


def test_ignored_terms_controller_uses_view_model_lookup_for_editing_selected_term() -> None:
    page = IgnoredTermsPageSpy()
    selected_term = IgnoredTermDto(
        id=4,
        term="live",
        scope="title",
        language="global",
        is_active=True,
    )
    view_model = IgnoredTermsViewModelSpy(selected_term)
    shown_pages: list[tuple[str, bool]] = []
    controller = IgnoredTermsController(
        page=page,
        view_model=view_model,
        show_page=lambda page_name, focus_input: shown_pages.append((page_name, focus_input)),
        on_action_recorded=lambda _message: None,
    )

    controller._handleEditTermById(4)

    assert view_model.find_calls == [4]
    assert page.term_text == "live"
    assert page.term_scope == "title"
    assert page.term_language == "global"
    assert page.save_mode is True
    assert shown_pages == [("ignoredTerms", True)]
    assert page.status_messages[-1] == ('Editando el termino "live".', "info")


def test_youtube_playlists_controller_does_not_reactivate_active_playlist() -> None:
    page = YoutubePlaylistsPageSpy()
    active_playlist = YoutubePlaylistDto(
        id=9,
        title="Favoritas",
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        is_active=True,
    )
    view_model = YoutubePlaylistsViewModelSpy(active_playlist)
    controller = YoutubePlaylistsController(
        page=page,
        view_model=view_model,
        import_view_model=YoutubePlaylistImportViewModelSpy(),
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_playlist_changed=lambda _title: None,
    )

    controller._handleActivatePlaylistById(9)

    assert view_model.find_calls == [9]
    assert view_model.activate_calls == []
    assert page.status_messages[-1] == ('La playlist "Favoritas" ya esta activa.', "info")


def test_youtube_playlists_controller_registers_primary_import_action() -> None:
    page = YoutubePlaylistsPageSpy()
    controller = YoutubePlaylistsController(
        page=page,
        view_model=YoutubePlaylistsViewModelSpy(None),
        import_view_model=YoutubePlaylistImportViewModelSpy(),
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_playlist_changed=lambda _title: None,
    )

    controller.bindEvents()

    assert page.primaryActionRequested.callback is not None


def test_youtube_playlists_controller_delegates_import_and_shows_feedback() -> None:
    page = YoutubePlaylistsPageSpy()
    active_playlist = YoutubePlaylistDto(
        id=9,
        title="Favoritas",
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        is_active=True,
    )
    import_view_model = YoutubePlaylistImportViewModelSpy(
        feedbacks=[
            YoutubePlaylistImportFeedback(
                status_message='Importando items de la playlist "Favoritas"...',
                status_tone="info",
            ),
            YoutubePlaylistImportFeedback(
                status_message='Importacion completada en "Favoritas": 42 items importados, 3 anadidos, 2 actualizados y 1 eliminados.',
                status_tone="success",
                last_action_message='Importacion completada en "Favoritas": 42 items importados, 3 anadidos, 2 actualizados y 1 eliminados.',
            ),
        ]
    )
    recorded_actions: list[str] = []
    controller = YoutubePlaylistsController(
        page=page,
        view_model=YoutubePlaylistsViewModelSpy(active_playlist),
        import_view_model=import_view_model,
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: recorded_actions.append("invalidate"),
        on_action_recorded=recorded_actions.append,
        on_active_playlist_changed=lambda _title: None,
    )

    controller._handleImportPlaylistItemsRequested()

    assert import_view_model.request_calls == 1
    assert import_view_model.received_active_playlist == active_playlist
    assert page.status_messages == [
        ('Importando items de la playlist "Favoritas"...', "info"),
        ('Importacion completada en "Favoritas": 42 items importados, 3 anadidos, 2 actualizados y 1 eliminados.', "success"),
    ]
    assert recorded_actions == [
        "invalidate",
        'Importacion completada en "Favoritas": 42 items importados, 3 anadidos, 2 actualizados y 1 eliminados.'
    ]


def test_youtube_playlists_controller_does_not_trigger_import_on_load_for_active_playlist() -> None:
    page = YoutubePlaylistsPageSpy()
    active_playlist = YoutubePlaylistDto(
        id=9,
        title="Favoritas",
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        is_active=True,
    )
    import_view_model = YoutubePlaylistImportViewModelSpy()
    controller = YoutubePlaylistsController(
        page=page,
        view_model=YoutubePlaylistsViewModelSpy(active_playlist),
        import_view_model=import_view_model,
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_playlist_changed=lambda _title: None,
    )

    controller.load()

    assert import_view_model.request_calls == 0
    assert import_view_model.received_active_playlist is None


def test_youtube_playlists_controller_does_not_trigger_auto_import_on_load_without_active_playlist() -> None:
    page = YoutubePlaylistsPageSpy()
    import_view_model = YoutubePlaylistImportViewModelSpy()
    controller = YoutubePlaylistsController(
        page=page,
        view_model=YoutubePlaylistsViewModelSpy(None),
        import_view_model=import_view_model,
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_comparison_data_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_playlist_changed=lambda _title: None,
    )

    controller.load()

    assert import_view_model.request_calls == 0


def test_comparison_controller_request_comparison_loads_local_songs_and_matching_results_into_page() -> None:
    page = ComparisonPageSpy()
    active_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Active",
        display_name="Active",
        is_active=True,
    )
    active_playlist = YoutubePlaylistDto(
        id=9,
        title="Favoritas",
        playlist_url="https://www.youtube.com/playlist?list=PL123",
        external_playlist_id="PL123",
        is_active=True,
    )
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=7,
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
                score=98.0,
                reason="Coincidencia fuerte en titulo y artista normalizados.",
            )
        ],
    )
    comparison_history = [
        PlaylistComparisonHistoryEntryDto(
            comparison_id=4,
            compared_at=datetime(2026, 6, 8, 12, 30, tzinfo=UTC),
            found_count=1,
            missing_count=0,
            possible_match_count=0,
            total_compared=1,
        )
    ]
    view_model = LibraryComparisonViewModelSpy(
        feedbacks=[
            LibraryComparisonFeedback(
                status_message="Comparando biblioteca local contra playlist activa...",
                status_tone="info",
            ),
            LibraryComparisonFeedback(
                status_message="Comparacion completada: 1 encontradas, 0 posibles coincidencias y 0 faltan.",
                status_tone="success",
                local_songs=local_songs,
                comparison_result=comparison_result,
                comparison_history=comparison_history,
                last_action_message="Comparacion completada: 1 encontradas, 0 posibles coincidencias y 0 faltan.",
            ),
        ]
    )
    context = ActiveComparisonContextSpy(folder=active_folder, playlist=active_playlist)
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.requestComparison()

    assert page.confirmation_requests == 1
    assert page.confirmation_payloads == [("Favoritas", "Active")]
    assert view_model.request_calls == 1
    assert page.loading_messages == [
        'Recalculando la comparacion entre "Favoritas" y "Active"...'
    ]
    assert page.loading_hidden == 1
    assert page.primary_action_labels[-1] == "↻ Refrescar"
    assert page.local_songs == local_songs
    assert page.comparison_result == comparison_result
    assert page.comparison_history == comparison_history
    assert page.status_messages == [
        ("Comparando biblioteca local contra playlist activa...", "info"),
        ("Comparacion completada: 1 encontradas, 0 posibles coincidencias y 0 faltan.", "success"),
    ]


def test_comparison_controller_request_comparison_shows_error_feedback_when_comparison_fails() -> None:
    page = ComparisonPageSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    view_model = LibraryComparisonViewModelSpy(
        feedbacks=[
            LibraryComparisonFeedback(
                status_message="Comparando biblioteca local contra playlist activa...",
                status_tone="info",
            ),
            LibraryComparisonFeedback(
                status_message="No hay una biblioteca local activa para comparar.",
                status_tone="error",
            ),
        ]
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.requestComparison()

    assert page.confirmation_requests == 1
    assert view_model.request_calls == 1
    assert page.loading_messages == [
        "Recalculando resultados y actualizando la base de datos..."
    ]
    assert page.loading_hidden == 1
    assert page.local_songs is None
    assert page.comparison_result is None
    assert page.status_messages == [
        ("Comparando biblioteca local contra playlist activa...", "info"),
        ("No hay una biblioteca local activa para comparar.", "error"),
    ]


def test_comparison_controller_request_comparison_does_nothing_when_user_cancels_confirmation() -> None:
    page = ComparisonPageSpy(confirms_comparison=False)
    view_model = LibraryComparisonViewModelSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.requestComparison()

    assert page.confirmation_requests == 1
    assert view_model.request_calls == 0
    assert page.loading_messages == []
    assert page.loading_hidden == 0


def test_comparison_controller_reuses_cached_results_without_reloading() -> None:
    page = ComparisonPageSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=7,
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
    view_model = LibraryComparisonViewModelSpy(
        cached_local_songs=local_songs,
        cached_comparison_result=comparison_result,
        cached_comparison_history=[
            PlaylistComparisonHistoryEntryDto(
                comparison_id=8,
                compared_at=datetime(2026, 6, 8, 9, 0, tzinfo=UTC),
                found_count=1,
                missing_count=0,
                possible_match_count=0,
                total_compared=1,
            )
        ],
        is_stale=False,
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.load()

    assert view_model.restore_calls == 0
    assert view_model.request_calls == 0
    assert page.loading_messages == []
    assert page.loading_hidden == 0
    assert page.local_songs == local_songs
    assert page.comparison_result == comparison_result
    assert len(page.comparison_history) == 1
    assert page.status_messages == []


def test_comparison_controller_load_shows_manual_message_without_cached_results() -> None:
    page = ComparisonPageSpy()
    view_model = LibraryComparisonViewModelSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.load()

    assert view_model.restore_calls == 1
    assert view_model.request_calls == 0
    assert page.loading_messages == []
    assert page.primary_action_labels == ["↻ Refrescar"]
    assert page.status_messages == [
        (
            'Pulsa "Refrescar comparacion" para calcular la comparacion y guardar el resultado actualizado.',
            "info",
        )
    ]


def test_comparison_controller_load_restores_persisted_results_when_memory_cache_is_empty() -> None:
    page = ComparisonPageSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=7,
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
    view_model = LibraryComparisonViewModelSpy(
        persisted_local_songs=local_songs,
        persisted_comparison_result=comparison_result,
        persisted_comparison_history=[
            PlaylistComparisonHistoryEntryDto(
                comparison_id=10,
                compared_at=datetime(2026, 6, 8, 8, 45, tzinfo=UTC),
                found_count=1,
                missing_count=0,
                possible_match_count=0,
                total_compared=1,
            )
        ],
        is_stale=False,
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.load()

    assert view_model.restore_calls == 1
    assert page.local_songs == local_songs
    assert page.comparison_result == comparison_result
    assert len(page.comparison_history) == 1
    assert page.status_messages == []


def test_comparison_controller_load_keeps_stale_cache_without_reloading() -> None:
    page = ComparisonPageSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    local_songs = [
        LocalSongDto(
            id=1,
            local_folder_id=7,
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
    view_model = LibraryComparisonViewModelSpy(
        cached_local_songs=local_songs,
        cached_comparison_result=comparison_result,
        cached_comparison_history=[
            PlaylistComparisonHistoryEntryDto(
                comparison_id=12,
                compared_at=datetime(2026, 6, 8, 7, 15, tzinfo=UTC),
                found_count=1,
                missing_count=0,
                possible_match_count=0,
                total_compared=1,
            )
        ],
        is_stale=True,
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.load()

    assert view_model.request_calls == 0
    assert page.local_songs == local_songs
    assert page.comparison_result == comparison_result
    assert len(page.comparison_history) == 1
    assert page.primary_action_labels[-1] == "↻ Volver a comparar"
    assert page.status_messages == [
        (
            'La biblioteca o la playlist activas han cambiado. Pulsa "Volver a comparar" para recalcular los resultados con el estado mas reciente.',
            "info",
        )
    ]


def test_comparison_controller_load_explains_missing_active_context() -> None:
    page = ComparisonPageSpy()
    view_model = LibraryComparisonViewModelSpy()
    context = ActiveComparisonContextSpy()
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.load()

    assert view_model.restore_calls == 0
    assert page.status_messages == [
        (
            "Activa una playlist de YouTube y una biblioteca local para ejecutar la comparacion.",
            "info",
        )
    ]


def test_comparison_controller_request_comparison_requires_active_playlist_and_folder() -> None:
    page = ComparisonPageSpy()
    view_model = LibraryComparisonViewModelSpy()
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        )
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.requestComparison()

    assert page.confirmation_requests == 0
    assert view_model.request_calls == 0
    assert page.loading_messages == []
    assert page.status_messages == [
        ("Activa una playlist de YouTube para ejecutar la comparacion.", "error")
    ]


def test_comparison_controller_invalidate_prompts_user_to_rerun_comparison_after_data_changes() -> None:
    page = ComparisonPageSpy()
    view_model = LibraryComparisonViewModelSpy(
        cached_comparison_result=PlaylistComparisonResultDto(
            summary=PlaylistComparisonSummaryDto(
                found_count=1,
                missing_count=0,
                possible_match_count=0,
                total_compared=1,
            ),
            items=[],
        ),
        is_stale=False,
    )
    context = ActiveComparisonContextSpy(
        folder=LocalFolderDto(
            id=7,
            path=r"C:\Music\Active",
            display_name="Active",
            is_active=True,
        ),
        playlist=YoutubePlaylistDto(
            id=9,
            title="Favoritas",
            playlist_url="https://www.youtube.com/playlist?list=PL123",
            external_playlist_id="PL123",
            is_active=True,
        ),
    )
    controller = ComparisonController(
        page=page,
        view_model=view_model,
        load_active_folder=context.load_active_folder,
        load_active_playlist=context.load_active_playlist,
    )

    controller.invalidate()

    assert view_model.invalidate_calls == 1
    assert page.primary_action_labels == ["↻ Volver a comparar"]
    assert page.status_messages == [
        (
            'La biblioteca o la playlist activas han cambiado. Pulsa "Volver a comparar" para recalcular los resultados con el estado mas reciente.',
            "info",
        )
    ]
