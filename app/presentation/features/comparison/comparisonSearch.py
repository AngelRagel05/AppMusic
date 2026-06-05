from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)


def filterLocalSongsByQuery(
    local_songs: list[LocalSongDto],
    query: str,
) -> list[LocalSongDto]:
    normalized_query = _normalizeQuery(query)
    if not normalized_query:
        return list(local_songs)

    return [
        local_song
        for local_song in local_songs
        if _matchesQuery(
            normalized_query,
            (
                local_song.title,
                local_song.artist,
                local_song.album,
                local_song.file_name,
            ),
        )
    ]


def filterComparisonItemsByQuery(
    comparison_items: list[PlaylistComparisonItemResultDto],
    query: str,
) -> list[PlaylistComparisonItemResultDto]:
    normalized_query = _normalizeQuery(query)
    if not normalized_query:
        return list(comparison_items)

    return [
        comparison_item
        for comparison_item in comparison_items
        if _matchesQuery(
            normalized_query,
            (
                comparison_item.youtube_title,
                comparison_item.youtube_artist,
                comparison_item.local_title,
                comparison_item.local_artist,
                comparison_item.reason,
            ),
        )
    ]


def _normalizeQuery(query: str) -> list[str]:
    return [token for token in query.lower().strip().split() if token]


def _matchesQuery(query_tokens: list[str], values: tuple[str | None, ...]) -> bool:
    searchable_text = " ".join(value.lower() for value in values if value)
    return all(token in searchable_text for token in query_tokens)
