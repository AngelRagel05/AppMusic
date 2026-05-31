from __future__ import annotations

import pytest

from app.application.dto.activateYoutubePlaylistInputDto import (
    ActivateYoutubePlaylistInputDto,
)
from app.application.dto.defineMainYoutubePlaylistInputDto import (
    DefineMainYoutubePlaylistInputDto,
)
from app.application.use_cases.activateYoutubePlaylistUseCase import (
    ActivateYoutubePlaylistUseCase,
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
from app.domain.entities.youtubePlaylist import YoutubePlaylist
from app.domain.services.youtubePlaylistRepository import YoutubePlaylistRepository


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


def test_define_main_youtube_playlist_use_case_persists_playlist_as_active() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    youtube_playlist = use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="  https://www.youtube.com/playlist?list=PL1234567890  "
        )
    )

    assert youtube_playlist.playlist_url == "https://www.youtube.com/playlist?list=PL1234567890"
    assert youtube_playlist.external_playlist_id == "PL1234567890"
    assert youtube_playlist.title == "Playlist PL1234567890"
    assert youtube_playlist.is_active is True


def test_define_main_youtube_playlist_use_case_rejects_non_youtube_url() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    with pytest.raises(ValueError, match="no pertenece a YouTube"):
        use_case.execute(
            DefineMainYoutubePlaylistInputDto(
                playlist_url="https://open.spotify.com/playlist/123"
            )
        )


def test_define_main_youtube_playlist_use_case_rejects_url_without_list_parameter() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = DefineMainYoutubePlaylistUseCase(repository)

    with pytest.raises(ValueError, match="parametro list"):
        use_case.execute(
            DefineMainYoutubePlaylistInputDto(
                playlist_url="https://www.youtube.com/watch?v=abc123"
            )
        )


def test_get_active_youtube_playlist_use_case_returns_none_when_no_playlist_is_active() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    use_case = GetActiveYoutubePlaylistUseCase(repository)

    assert use_case.execute() is None


def test_list_youtube_playlists_use_case_returns_saved_playlists() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    define_use_case = DefineMainYoutubePlaylistUseCase(repository)
    list_use_case = ListYoutubePlaylistsUseCase(repository)

    define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLFIRST"
        )
    )
    define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://music.youtube.com/playlist?list=PLSECOND"
        )
    )

    youtube_playlists = list_use_case.execute()

    assert len(youtube_playlists) == 2
    assert {youtube_playlist.external_playlist_id for youtube_playlist in youtube_playlists} == {
        "PLFIRST",
        "PLSECOND",
    }


def test_activate_youtube_playlist_use_case_switches_active_playlist() -> None:
    repository = InMemoryYoutubePlaylistRepository()
    define_use_case = DefineMainYoutubePlaylistUseCase(repository)
    activate_use_case = ActivateYoutubePlaylistUseCase(repository)

    first_playlist = define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLFIRST"
        )
    )
    define_use_case.execute(
        DefineMainYoutubePlaylistInputDto(
            playlist_url="https://www.youtube.com/playlist?list=PLSECOND"
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
