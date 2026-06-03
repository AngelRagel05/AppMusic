from __future__ import annotations

from app.application.dto.activateYoutubePlaylistInputDto import (
    ActivateYoutubePlaylistInputDto,
)
from app.application.dto.deleteYoutubePlaylistInputDto import (
    DeleteYoutubePlaylistInputDto,
)
from app.application.dto.defineMainYoutubePlaylistInputDto import (
    DefineMainYoutubePlaylistInputDto,
)
from app.application.dto.updateYoutubePlaylistInputDto import (
    UpdateYoutubePlaylistInputDto,
)
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.application.use_cases import (
    ActivateYoutubePlaylistUseCase,
    DefineMainYoutubePlaylistUseCase,
    DeleteYoutubePlaylistUseCase,
    GetActiveYoutubePlaylistUseCase,
    ListYoutubePlaylistsUseCase,
    UpdateYoutubePlaylistUseCase,
)


class YoutubePlaylistViewModel:
    def __init__(
        self,
        list_use_case: ListYoutubePlaylistsUseCase,
        get_active_use_case: GetActiveYoutubePlaylistUseCase,
        activate_use_case: ActivateYoutubePlaylistUseCase,
        define_main_use_case: DefineMainYoutubePlaylistUseCase,
        update_use_case: UpdateYoutubePlaylistUseCase,
        delete_use_case: DeleteYoutubePlaylistUseCase,
    ) -> None:
        self._list_use_case = list_use_case
        self._get_active_use_case = get_active_use_case
        self._activate_use_case = activate_use_case
        self._define_main_use_case = define_main_use_case
        self._update_use_case = update_use_case
        self._delete_use_case = delete_use_case
        self._playlists_cache: list[YoutubePlaylistDto] = []
        self._playlists_by_id: dict[int, YoutubePlaylistDto] = {}
        self._active_playlist_cache: YoutubePlaylistDto | None = None

    def refreshState(self) -> tuple[list[YoutubePlaylistDto], YoutubePlaylistDto | None]:
        playlists = self._list_use_case.execute()
        activePlaylist = self._get_active_use_case.execute()
        self._storePlaylists(playlists)
        self._active_playlist_cache = activePlaylist
        return playlists, activePlaylist

    def load_playlists(self) -> list[YoutubePlaylistDto]:
        if not self._playlists_cache:
            self.refreshState()
        return list(self._playlists_cache)

    def load_active_playlist(self) -> YoutubePlaylistDto | None:
        if self._active_playlist_cache is None and not self._playlists_cache:
            self.refreshState()
        return self._active_playlist_cache

    def find_playlist_by_id(self, youtube_playlist_id: int) -> YoutubePlaylistDto | None:
        if not self._playlists_cache:
            self.refreshState()
        return self._playlists_by_id.get(youtube_playlist_id)

    def activate_playlist(self, youtube_playlist_id: int) -> YoutubePlaylistDto:
        youtubePlaylist = self._activate_use_case.execute(
            ActivateYoutubePlaylistInputDto(youtube_playlist_id=youtube_playlist_id)
        )
        self.refreshState()
        return youtubePlaylist

    def define_main_playlist(self, playlist_url: str, title: str) -> YoutubePlaylistDto:
        youtubePlaylist = self._define_main_use_case.execute(
            DefineMainYoutubePlaylistInputDto(playlist_url=playlist_url, title=title)
        )
        self.refreshState()
        return youtubePlaylist

    def update_playlist(
        self,
        youtube_playlist_id: int,
        playlist_url: str,
        title: str,
    ) -> YoutubePlaylistDto:
        youtubePlaylist = self._update_use_case.execute(
            UpdateYoutubePlaylistInputDto(
                youtube_playlist_id=youtube_playlist_id,
                playlist_url=playlist_url,
                title=title,
            )
        )
        self.refreshState()
        return youtubePlaylist

    def delete_playlist(self, youtube_playlist_id: int) -> None:
        self._delete_use_case.execute(
            DeleteYoutubePlaylistInputDto(youtube_playlist_id=youtube_playlist_id)
        )
        self.refreshState()

    def _storePlaylists(self, playlists: list[YoutubePlaylistDto]) -> None:
        self._playlists_cache = list(playlists)
        self._playlists_by_id = {playlist.id: playlist for playlist in playlists}
