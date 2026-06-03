from __future__ import annotations

from app.application.dto.deleteYoutubePlaylistInputDto import DeleteYoutubePlaylistInputDto
from app.application.validators.playlists.youtubePlaylistValidators import (
    validateYoutubePlaylistId,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)


class DeleteYoutubePlaylistUseCase:
    def __init__(self, repository: YoutubePlaylistRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DeleteYoutubePlaylistInputDto) -> None:
        validateYoutubePlaylistId(input_dto.youtube_playlist_id)
        self._repository.delete(input_dto.youtube_playlist_id)
