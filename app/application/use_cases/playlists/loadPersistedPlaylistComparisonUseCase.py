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
from app.domain.playlists.services import (
    AUTO_AMBIGUOUS,
    AUTO_NO_COMPETITIVE_CANDIDATE,
    AUTO_TITLE_ARTIST_DURATION,
    MANUAL_USER_LINKED_LOCAL_SONG,
    MANUAL_USER_MARKED_FOUND,
    MANUAL_USER_MARKED_MISSING,
    MANUAL_USER_MARKED_POSSIBLE,
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
        linked_local_song_by_id = _buildLinkedLocalSongLookup(
            comparison_rows,
            local_song_by_id,
            self._local_song_repository,
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
                local_title=_resolveLocalTitle(linked_local_song_by_id.get(row.local_song_id)),
                local_artist=_resolveLocalArtist(linked_local_song_by_id.get(row.local_song_id)),
                score=float(row.score or 0.0),
                reason=_buildPersistedReason(row.match_status, row.score, row.matched_by),
                matched_by=row.matched_by,
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
        return local_songs, PlaylistComparisonResultDto(
            summary=summary,
            items=comparison_items,
            playlist_comparison_id=persisted_comparison.id,
            last_compared_at=persisted_comparison.compared_at,
        )


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


def _buildLinkedLocalSongLookup(
    comparison_rows,
    available_local_song_by_id: dict[int, LocalSongDto],
    local_song_repository: LocalSongRepository,
) -> dict[int, LocalSongDto]:
    linked_local_song_by_id = dict(available_local_song_by_id)
    missing_local_song_ids = {
        row.local_song_id
        for row in comparison_rows
        if row.local_song_id is not None and row.local_song_id not in linked_local_song_by_id
    }
    for local_song_id in missing_local_song_ids:
        persisted_local_song = local_song_repository.get_by_id(local_song_id)
        if persisted_local_song is None:
            continue
        linked_local_song_by_id[local_song_id] = LocalSongDto(
            id=persisted_local_song.id or 0,
            local_folder_id=persisted_local_song.local_folder_id or 0,
            file_path=persisted_local_song.file_path,
            file_name=persisted_local_song.file_name,
            is_available=persisted_local_song.is_available,
            title=persisted_local_song.title,
            artist=persisted_local_song.artist,
            album=persisted_local_song.album,
            release_year=persisted_local_song.release_year,
            track_number_album=persisted_local_song.track_number_album,
            duration_seconds=persisted_local_song.duration_seconds,
        )
    return linked_local_song_by_id


def _buildPersistedReason(
    match_status: str,
    score: float | None,
    persisted_reason: str | None,
) -> str:
    normalized_reason = (persisted_reason or "").strip()
    if normalized_reason:
        mapped_reason = _mapMatchedByToReason(normalized_reason, match_status)
        if mapped_reason is not None:
            return mapped_reason
        return normalized_reason

    status = ComparisonStatus(match_status)
    normalized_score = float(score or 0.0)
    if status is ComparisonStatus.FOUND:
        return f"Coincidencia encontrada en snapshot persistido. Score {normalized_score:.1f}."
    if status is ComparisonStatus.POSSIBLE_MATCH:
        return (
            "Posible coincidencia rehidratada desde snapshot persistido. "
            f"Score {normalized_score:.1f}."
        )
    return "Sin coincidencia concreta rehidratada desde snapshot persistido."


def _mapMatchedByToReason(
    matched_by: str,
    match_status: str,
) -> str | None:
    if matched_by == AUTO_TITLE_ARTIST_DURATION:
        return "Coincidencia confirmada por titulo y artista validos."
    if matched_by == AUTO_AMBIGUOUS:
        return "Varias candidatas comparten titulo y artista; no se puede resolver de forma automatica."
    if matched_by == AUTO_NO_COMPETITIVE_CANDIDATE:
        return "No hay candidata suficientemente competitiva."
    if matched_by == MANUAL_USER_LINKED_LOCAL_SONG:
        return "Enlace manual con cancion local decidido por el usuario."
    if matched_by == MANUAL_USER_MARKED_FOUND:
        return "Marcado manualmente como encontrada por el usuario."
    if matched_by == MANUAL_USER_MARKED_MISSING:
        return "Marcado manualmente como faltante por el usuario."
    if matched_by == MANUAL_USER_MARKED_POSSIBLE:
        return "Marcado manualmente como posible coincidencia por el usuario."
    return None
