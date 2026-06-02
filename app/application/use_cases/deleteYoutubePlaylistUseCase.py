from __future__ import annotations

from app.application.dto.deleteYoutubePlaylistInputDto import DeleteYoutubePlaylistInputDto
from app.domain.services.youtubePlaylistRepository import YoutubePlaylistRepository


class DeleteYoutubePlaylistUseCase:
    def __init__(self, repository: YoutubePlaylistRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DeleteYoutubePlaylistInputDto) -> None:
        if input_dto.youtube_playlist_id <= 0:
            msg = "La playlist seleccionada no es valida."
            raise ValueError(msg)

        self._repository.delete(input_dto.youtube_playlist_id)
