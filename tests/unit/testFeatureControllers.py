from __future__ import annotations

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.localFolderDto import LocalFolderDto
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.presentation.features.ignoredTerms.controller.ignoredTermsController import (
    IgnoredTermsController,
)
from app.presentation.features.localLibrary.controller.localLibraryController import (
    LocalLibraryController,
)
from app.presentation.viewmodels.localLibrary.localLibraryScanViewModel import (
    LocalLibraryScanFeedback,
)
from app.presentation.features.youtubePlaylists.controller.youtubePlaylistsController import (
    YoutubePlaylistsController,
)


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
        return [], None

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
        self.saveRequested = PageCallbackPort()
        self.activateRequested = PageCallbackPort()
        self.editRequested = PageCallbackPort()
        self.deleteRequested = PageCallbackPort()
        self.playlist_title = ""
        self.playlist_url = ""
        self.save_mode = None
        self.status_messages: list[tuple[str, str]] = []

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


class YoutubePlaylistsViewModelSpy:
    def __init__(self, selected_playlist: YoutubePlaylistDto | None) -> None:
        self.selected_playlist = selected_playlist
        self.find_calls: list[int] = []
        self.activate_calls: list[int] = []

    def refreshState(self):
        return [], None

    def load_playlists(self):
        raise AssertionError("load_playlists no debe usarse para buscar por id")

    def load_active_playlist(self):
        return None

    def find_playlist_by_id(self, youtube_playlist_id: int):
        self.find_calls.append(youtube_playlist_id)
        return self.selected_playlist

    def activate_playlist(self, youtube_playlist_id: int):
        self.activate_calls.append(youtube_playlist_id)
        return self.selected_playlist


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
                status_message='Escaneo completado en "Jazz": 2 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas).',
                status_tone="success",
                song_count_label="2 MP3 detectados",
                last_action_message='Escaneo completado en "Jazz": 2 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas).',
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
        on_action_recorded=recorded_actions.append,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=song_count_updates.append,
    )

    controller._handleScanLibraryRequested()

    assert scan_view_model.request_calls == 1
    assert scan_view_model.received_active_folder == active_folder
    assert song_count_updates == ["Escaneando...", "2 MP3 detectados"]
    assert recorded_actions[-1] == 'Escaneo completado en "Jazz": 2 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas).'
    assert page.status_messages[0] == ('Escaneando la biblioteca "Jazz"...', "info")
    assert page.status_messages[-1] == (
        'Escaneo completado en "Jazz": 2 MP3 detectados, 2 canciones registradas (1 nuevas y 1 ya registradas).',
        "success",
    )


def test_local_library_controller_delegates_manual_refresh_of_scanned_songs() -> None:
    page = LocalLibraryPageSpy()
    active_folder = LocalFolderDto(
        id=7,
        path=r"C:\Music\Jazz",
        display_name="Jazz",
        is_active=True,
    )
    scan_view_model = LocalLibraryScanViewModelSpy()
    controller = LocalLibraryController(
        page=page,
        view_model=LocalLibraryViewModelSpy(active_folder),
        scan_view_model=scan_view_model,
        folder_monitor_worker=LocalFolderMonitorWorkerSpy(),
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_folder_changed=lambda _name: None,
        on_song_count_changed=lambda _value: None,
    )

    controller.bindEvents()
    if page.secondaryActionRequested.callback is None:
        raise AssertionError("Se esperaba callback secundario registrado.")

    page.secondaryActionRequested.callback()

    assert scan_view_model.request_calls == 1
    assert scan_view_model.received_active_folder == active_folder


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
        show_page=lambda _page_name, _focus_input: None,
        on_state_changed=lambda: None,
        on_action_recorded=lambda _message: None,
        on_active_playlist_changed=lambda _title: None,
    )

    controller._handleActivatePlaylistById(9)

    assert view_model.find_calls == [9]
    assert view_model.activate_calls == []
    assert page.status_messages[-1] == ('La playlist "Favoritas" ya esta activa.', "info")
