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
from app.application.use_cases.activateYoutubePlaylistUseCase import (
    ActivateYoutubePlaylistUseCase,
)
from app.application.use_cases.deleteYoutubePlaylistUseCase import (
    DeleteYoutubePlaylistUseCase,
)
from app.application.use_cases.defineMainYoutubePlaylistUseCase import (
    DefineMainYoutubePlaylistUseCase,
)
from app.application.use_cases.getActiveYoutubePlaylistUseCase import (
    GetActiveYoutubePlaylistUseCase,
)
from app.application.use_cases.listYoutubePlaylistsUseCase import (
    ListYoutubePlaylistsUseCase,
)
from app.application.use_cases.updateYoutubePlaylistUseCase import (
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

    def load_playlists(self) -> list[YoutubePlaylistDto]:
        return self._list_use_case.execute()

    def load_active_playlist(self) -> YoutubePlaylistDto | None:
        return self._get_active_use_case.execute()

    def activate_playlist(self, youtube_playlist_id: int) -> YoutubePlaylistDto:
        return self._activate_use_case.execute(
            ActivateYoutubePlaylistInputDto(youtube_playlist_id=youtube_playlist_id)
        )

    def define_main_playlist(self, playlist_url: str, title: str) -> YoutubePlaylistDto:
        return self._define_main_use_case.execute(
            DefineMainYoutubePlaylistInputDto(playlist_url=playlist_url, title=title)
        )

    def update_playlist(
        self,
        youtube_playlist_id: int,
        playlist_url: str,
        title: str,
    ) -> YoutubePlaylistDto:
        return self._update_use_case.execute(
            UpdateYoutubePlaylistInputDto(
                youtube_playlist_id=youtube_playlist_id,
                playlist_url=playlist_url,
                title=title,
            )
        )

    def delete_playlist(self, youtube_playlist_id: int) -> None:
        self._delete_use_case.execute(
            DeleteYoutubePlaylistInputDto(youtube_playlist_id=youtube_playlist_id)
        )
