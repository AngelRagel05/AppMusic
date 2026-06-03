from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

CANONICAL_YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list={playlist_id}"
VALID_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


@dataclass(frozen=True)
class NormalizedYoutubePlaylistData:
    playlist_url: str
    external_playlist_id: str
    title: str


def validateYoutubePlaylistId(youtube_playlist_id: int) -> None:
    if youtube_playlist_id <= 0:
        msg = "La playlist seleccionada no es valida."
        raise ValueError(msg)


def normalizeYoutubePlaylistData(
    playlist_url: str,
    title: str,
) -> NormalizedYoutubePlaylistData:
    normalized_url = playlist_url.strip()
    if not normalized_url:
        msg = "La playlist principal no puede estar vacia."
        raise ValueError(msg)

    normalized_title = title.strip()
    if not normalized_title:
        msg = "El nombre de la playlist no puede estar vacio."
        raise ValueError(msg)

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
