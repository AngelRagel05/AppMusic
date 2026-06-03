from __future__ import annotations

from app.application.dto.defineMainYoutubePlaylistInputDto import (
    DefineMainYoutubePlaylistInputDto,
)
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.application.validators.playlists.youtubePlaylistValidators import (
    normalizeYoutubePlaylistData,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)


class DefineMainYoutubePlaylistUseCase:
    def __init__(self, repository: YoutubePlaylistRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DefineMainYoutubePlaylistInputDto) -> YoutubePlaylistDto:
        normalized_data = normalizeYoutubePlaylistData(
            playlist_url=input_dto.playlist_url,
            title=input_dto.title,
        )
        youtube_playlist = self._repository.save_as_active(
            playlist_url=normalized_data.playlist_url,
            external_playlist_id=normalized_data.external_playlist_id,
            title=normalized_data.title,
        )
        return YoutubePlaylistDto(
            id=youtube_playlist.id or 0,
            playlist_url=youtube_playlist.playlist_url,
            external_playlist_id=youtube_playlist.external_playlist_id,
            title=youtube_playlist.title,
            is_active=youtube_playlist.is_active,
        )
