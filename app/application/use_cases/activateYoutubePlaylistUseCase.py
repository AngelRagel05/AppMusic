from __future__ import annotations

from app.application.dto.activateYoutubePlaylistInputDto import (
    ActivateYoutubePlaylistInputDto,
)
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.domain.repositories.youtubePlaylistRepository import YoutubePlaylistRepository


class ActivateYoutubePlaylistUseCase:
    def __init__(self, repository: YoutubePlaylistRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: ActivateYoutubePlaylistInputDto) -> YoutubePlaylistDto:
        if input_dto.youtube_playlist_id <= 0:
            msg = "La playlist seleccionada no es valida."
            raise ValueError(msg)

        youtube_playlist = self._repository.activate(input_dto.youtube_playlist_id)
        return YoutubePlaylistDto(
            id=youtube_playlist.id or 0,
            playlist_url=youtube_playlist.playlist_url,
            external_playlist_id=youtube_playlist.external_playlist_id,
            title=youtube_playlist.title,
            is_active=youtube_playlist.is_active,
        )
