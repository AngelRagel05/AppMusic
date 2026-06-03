from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from app.shared.constants.youtube import (
    CANONICAL_YOUTUBE_PLAYLIST_URL,
    VALID_YOUTUBE_HOSTS,
)
from app.shared.exceptions import ValidationError


@dataclass(frozen=True)
class NormalizedYoutubePlaylistData:
    playlist_url: str
    external_playlist_id: str
    title: str


def validateYoutubePlaylistId(youtube_playlist_id: int) -> None:
    if youtube_playlist_id <= 0:
        msg = "La playlist seleccionada no es valida."
        raise ValidationError(msg)


def normalizeYoutubePlaylistData(
    playlist_url: str,
    title: str,
) -> NormalizedYoutubePlaylistData:
    normalized_url = playlist_url.strip()
    if not normalized_url:
        msg = "La playlist principal no puede estar vacia."
        raise ValidationError(msg)

    normalized_title = title.strip()
    if not normalized_title:
        msg = "El nombre de la playlist no puede estar vacio."
        raise ValidationError(msg)

    external_playlist_id = _extractPlaylistId(normalized_url)
    canonical_url = CANONICAL_YOUTUBE_PLAYLIST_URL.format(
        playlist_id=external_playlist_id
    )
    return NormalizedYoutubePlaylistData(
        playlist_url=canonical_url,
        external_playlist_id=external_playlist_id,
        title=normalized_title,
    )


def _extractPlaylistId(playlist_url: str) -> str:
    parsed_url = urlparse(playlist_url)
    if parsed_url.scheme not in {"http", "https"}:
        msg = "La URL de la playlist debe empezar por http o https."
        raise ValidationError(msg)

    host = parsed_url.netloc.lower()
    if host not in VALID_YOUTUBE_HOSTS:
        msg = "La URL indicada no pertenece a YouTube."
        raise ValidationError(msg)

    playlist_ids = parse_qs(parsed_url.query).get("list", [])
    playlist_id = playlist_ids[0].strip() if playlist_ids else ""
    if not playlist_id:
        msg = "La URL de la playlist debe incluir el parametro list."
        raise ValidationError(msg)

    return playlist_id
