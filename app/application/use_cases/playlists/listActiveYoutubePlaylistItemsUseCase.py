from __future__ import annotations

from app.application.dto.youtubePlaylistItemDto import YoutubePlaylistItemDto
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)


class ListActiveYoutubePlaylistItemsUseCase:
    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        youtube_playlist_item_repository: YoutubePlaylistItemRepository,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._youtube_playlist_item_repository = youtube_playlist_item_repository

    def execute(self) -> list[YoutubePlaylistItemDto]:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        if active_youtube_playlist is None or active_youtube_playlist.id is None:
            return []

        return [
            YoutubePlaylistItemDto(
                id=youtube_playlist_item.id or 0,
                youtube_playlist_id=youtube_playlist_item.youtube_playlist_id,
                external_video_id=youtube_playlist_item.external_video_id,
                position=youtube_playlist_item.position,
                raw_title=youtube_playlist_item.raw_title,
                raw_channel_name=youtube_playlist_item.raw_channel_name,
                normalized_title=youtube_playlist_item.normalized_title,
                normalized_artist=youtube_playlist_item.normalized_artist,
                duration_seconds=youtube_playlist_item.duration_seconds,
                published_at=youtube_playlist_item.published_at,
            )
            for youtube_playlist_item in self._youtube_playlist_item_repository.list_by_playlist(
                active_youtube_playlist.id
            )
        ]
