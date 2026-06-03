from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from app.application.dto.defineMainYoutubePlaylistInputDto import (
    DefineMainYoutubePlaylistInputDto,
)
from app.application.dto.youtubePlaylistDto import YoutubePlaylistDto
from app.domain.repositories.youtubePlaylistRepository import YoutubePlaylistRepository

CANONICAL_YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list={playlist_id}"
VALID_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


class DefineMainYoutubePlaylistUseCase:
    def __init__(self, repository: YoutubePlaylistRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DefineMainYoutubePlaylistInputDto) -> YoutubePlaylistDto:
        normalized_url = input_dto.playlist_url.strip()
        if not normalized_url:
            msg = "La playlist principal no puede estar vacia."
            raise ValueError(msg)

        normalized_title = input_dto.title.strip()
        if not normalized_title:
            msg = "El nombre de la playlist no puede estar vacio."
            raise ValueError(msg)

        external_playlist_id = self._extract_playlist_id(normalized_url)
        playlist_url = CANONICAL_YOUTUBE_PLAYLIST_URL.format(
            playlist_id=external_playlist_id
        )
        youtube_playlist = self._repository.save_as_active(
            playlist_url=playlist_url,
            external_playlist_id=external_playlist_id,
            title=normalized_title,
        )
        return YoutubePlaylistDto(
            id=youtube_playlist.id or 0,
            playlist_url=youtube_playlist.playlist_url,
            external_playlist_id=youtube_playlist.external_playlist_id,
            title=youtube_playlist.title,
            is_active=youtube_playlist.is_active,
        )

    def _extract_playlist_id(self, playlist_url: str) -> str:
        parsed_url = urlparse(playlist_url)
        if parsed_url.scheme not in {"http", "https"}:
            msg = "La URL de la playlist debe empezar por http o https."
            raise ValueError(msg)

        host = parsed_url.netloc.lower()
        if host not in VALID_YOUTUBE_HOSTS:
            msg = "La URL indicada no pertenece a YouTube."
            raise ValueError(msg)

        playlist_ids = parse_qs(parsed_url.query).get("list", [])
        playlist_id = playlist_ids[0].strip() if playlist_ids else ""
        if not playlist_id:
            msg = "La URL de la playlist debe incluir el parametro list."
            raise ValueError(msg)

        return playlist_id
