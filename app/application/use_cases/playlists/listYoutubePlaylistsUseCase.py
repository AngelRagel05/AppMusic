from __future__ import annotations

from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)


class ListYoutubePlaylistsUseCase:
    def __init__(self, repository: YoutubePlaylistRepository) -> None:
        self._repository = repository

    def execute(self) -> list[YoutubePlaylistDto]:
        return [
            YoutubePlaylistDto(
                id=youtube_playlist.id or 0,
                playlist_url=youtube_playlist.playlist_url,
                external_playlist_id=youtube_playlist.external_playlist_id,
                title=youtube_playlist.title,
                is_active=youtube_playlist.is_active,
            )
            for youtube_playlist in self._repository.list_all()
        ]
