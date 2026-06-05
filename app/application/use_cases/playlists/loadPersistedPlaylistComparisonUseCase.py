from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.playlistComparisonItemResultDto import (
    PlaylistComparisonItemResultDto,
)
from app.application.dto.playlistComparisonResultDto import PlaylistComparisonResultDto
from app.application.dto.playlistComparisonSummaryDto import PlaylistComparisonSummaryDto
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.playlists.repositories.playlistComparisonRepository import (
    PlaylistComparisonRepository,
)
from app.domain.playlists.repositories.playlistComparisonResultRepository import (
    PlaylistComparisonResultRepository,
)
from app.domain.playlists.repositories.youtubePlaylistItemRepository import (
    YoutubePlaylistItemRepository,
)
from app.domain.playlists.repositories.youtubePlaylistRepository import (
    YoutubePlaylistRepository,
)
from app.shared.constants.comparison import ComparisonStatus


class LoadPersistedPlaylistComparisonUseCase:
    def __init__(
        self,
        youtube_playlist_repository: YoutubePlaylistRepository,
        youtube_playlist_item_repository: YoutubePlaylistItemRepository,
        local_folder_repository: LocalFolderRepository,
        local_song_repository: LocalSongRepository,
        playlist_comparison_repository: PlaylistComparisonRepository,
        playlist_comparison_result_repository: PlaylistComparisonResultRepository,
    ) -> None:
        self._youtube_playlist_repository = youtube_playlist_repository
        self._youtube_playlist_item_repository = youtube_playlist_item_repository
        self._local_folder_repository = local_folder_repository
        self._local_song_repository = local_song_repository
        self._playlist_comparison_repository = playlist_comparison_repository
        self._playlist_comparison_result_repository = playlist_comparison_result_repository

    def execute(
        self,
    ) -> tuple[list[LocalSongDto], PlaylistComparisonResultDto] | None:
        active_youtube_playlist = self._youtube_playlist_repository.get_active()
        active_local_folder = self._local_folder_repository.get_active()
        if (
            active_youtube_playlist is None
            or active_youtube_playlist.id is None
            or active_local_folder is None
            or active_local_folder.id is None
        ):
            return None

        persisted_comparison = self._playlist_comparison_repository.find_latest_for_scope(
            active_youtube_playlist.id,
            active_local_folder.id,
        )
        if persisted_comparison is None or persisted_comparison.id is None:
            return None

        local_songs = [
            LocalSongDto(
                id=local_song.id or 0,
                local_folder_id=local_song.local_folder_id or 0,
                file_path=local_song.file_path,
                file_name=local_song.file_name,
                is_available=local_song.is_available,
                title=local_song.title,
                artist=local_song.artist,
                album=local_song.album,
                release_year=local_song.release_year,
                track_number_album=local_song.track_number_album,
                duration_seconds=local_song.duration_seconds,
            )
            for local_song in self._local_song_repository.list_by_folder(active_local_folder.id)
            if local_song.is_available
        ]
        local_song_by_id = {local_song.id: local_song for local_song in local_songs}
        youtube_items = self._youtube_playlist_item_repository.list_by_playlist(
            active_youtube_playlist.id
        )
        youtube_item_by_id = {youtube_item.id: youtube_item for youtube_item in youtube_items}

        comparison_rows = self._playlist_comparison_result_repository.list_by_comparison(
            persisted_comparison.id
        )
        comparison_items = [
            PlaylistComparisonItemResultDto(
                youtube_playlist_item_id=row.youtube_playlist_item_id,
                local_song_id=row.local_song_id,
                comparison_status=ComparisonStatus(row.match_status),
                youtube_title=_resolveYoutubeTitle(youtube_item_by_id.get(row.youtube_playlist_item_id)),
                youtube_artist=_resolveYoutubeArtist(
                    youtube_item_by_id.get(row.youtube_playlist_item_id)
                ),
                local_title=_resolveLocalTitle(local_song_by_id.get(row.local_song_id)),
                local_artist=_resolveLocalArtist(local_song_by_id.get(row.local_song_id)),
                score=float(row.score or 0.0),
                reason=_buildPersistedReason(row.match_status, row.score),
            )
            for row in comparison_rows
        ]
        summary = PlaylistComparisonSummaryDto(
            found_count=sum(
                1
                for item in comparison_items
                if item.comparison_status is ComparisonStatus.FOUND
            ),
            missing_count=sum(
                1
                for item in comparison_items
                if item.comparison_status is ComparisonStatus.MISSING
            ),
            possible_match_count=sum(
                1
                for item in comparison_items
                if item.comparison_status is ComparisonStatus.POSSIBLE_MATCH
            ),
            total_compared=len(comparison_items),
        )
        return local_songs, PlaylistComparisonResultDto(summary=summary, items=comparison_items)


def _resolveYoutubeTitle(youtube_item) -> str:
    if youtube_item is None:
        return "Item de YouTube no disponible"
    return youtube_item.raw_title or youtube_item.normalized_title


def _resolveYoutubeArtist(youtube_item) -> str:
    if youtube_item is None:
        return "Canal no disponible"
    return youtube_item.raw_channel_name or youtube_item.normalized_artist


def _resolveLocalTitle(local_song: LocalSongDto | None) -> str | None:
    if local_song is None:
        return None
    return local_song.title


def _resolveLocalArtist(local_song: LocalSongDto | None) -> str | None:
    if local_song is None:
        return None
    return local_song.artist


def _buildPersistedReason(match_status: str, score: float | None) -> str:
    status = ComparisonStatus(match_status)
    normalized_score = float(score or 0.0)
    if status is ComparisonStatus.FOUND:
        return f"Snapshot persistido con coincidencia encontrada. Score {normalized_score:.1f}."
    if status is ComparisonStatus.POSSIBLE_MATCH:
        return (
            "Snapshot persistido con posible coincidencia. "
            f"Score {normalized_score:.1f}."
        )
    return "Snapshot persistido sin coincidencia suficiente."
