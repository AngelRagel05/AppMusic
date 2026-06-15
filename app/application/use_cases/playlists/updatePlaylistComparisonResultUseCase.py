from __future__ import annotations

from app.application.dto.updatePlaylistComparisonResultInputDto import (
    UpdatePlaylistComparisonResultInputDto,
)
from app.domain.library.repositories.localSongRepository import LocalSongRepository
from app.domain.playlists.repositories.playlistComparisonRepository import (
    PlaylistComparisonRepository,
)
from app.domain.playlists.repositories.playlistComparisonResultRepository import (
    PlaylistComparisonResultRepository,
)
from app.domain.playlists.services import (
    MANUAL_USER_LINKED_LOCAL_SONG,
    MANUAL_USER_MARKED_FOUND,
    MANUAL_USER_MARKED_MISSING,
    MANUAL_USER_MARKED_POSSIBLE,
)
from app.shared.constants.comparison import ComparisonStatus


class UpdatePlaylistComparisonResultUseCase:
    def __init__(
        self,
        playlist_comparison_repository: PlaylistComparisonRepository,
        playlist_comparison_result_repository: PlaylistComparisonResultRepository,
        local_song_repository: LocalSongRepository,
    ) -> None:
        self._playlist_comparison_repository = playlist_comparison_repository
        self._playlist_comparison_result_repository = playlist_comparison_result_repository
        self._local_song_repository = local_song_repository

    def execute(
        self,
        input_dto: UpdatePlaylistComparisonResultInputDto,
    ) -> PlaylistComparisonResult:
        comparison = self._playlist_comparison_repository.find_by_id(
            input_dto.playlist_comparison_id
        )
        if comparison is None:
            raise ValueError("La comparacion seleccionada no existe.")

        existing_result = self._playlist_comparison_result_repository.find_by_comparison_item(
            input_dto.playlist_comparison_id,
            input_dto.youtube_playlist_item_id,
        )
        if existing_result is None:
            raise ValueError("El resultado de comparacion seleccionado no existe.")

        normalized_status = ComparisonStatus(input_dto.match_status)
        requested_local_song_id = (
            None
            if normalized_status is ComparisonStatus.MISSING
            else input_dto.local_song_id
        )
        validated_local_song_id = self._validateLocalSongSelection(
            comparison_local_folder_id=comparison.local_folder_id,
            local_song_id=requested_local_song_id,
        )
        if normalized_status is ComparisonStatus.FOUND and validated_local_song_id is None:
            raise ValueError("Para marcar como found debes seleccionar una cancion local.")
        matched_by = self._buildManualMatchedBy(
            status=normalized_status,
            existing_local_song_id=existing_result.local_song_id,
            updated_local_song_id=validated_local_song_id,
        )
        persisted_result = self._playlist_comparison_result_repository.update_match_decision(
            playlist_comparison_id=existing_result.playlist_comparison_id,
            youtube_playlist_item_id=existing_result.youtube_playlist_item_id,
            local_song_id=validated_local_song_id,
            match_status=normalized_status.value,
            matched_by=matched_by,
        )
        self._playlist_comparison_repository.commit()
        return persisted_result

    def _validateLocalSongSelection(
        self,
        *,
        comparison_local_folder_id: int,
        local_song_id: int | None,
    ) -> int | None:
        if local_song_id is None:
            return None

        local_song = self._local_song_repository.get_by_id(local_song_id)
        if local_song is None:
            raise ValueError("La cancion local seleccionada no existe.")
        if local_song.local_folder_id != comparison_local_folder_id:
            raise ValueError(
                "La cancion local seleccionada no pertenece a la biblioteca del snapshot."
            )
        return local_song_id

    def _buildManualMatchedBy(
        self,
        *,
        status: ComparisonStatus,
        existing_local_song_id: int | None,
        updated_local_song_id: int | None,
    ) -> str:
        if updated_local_song_id is not None and updated_local_song_id != existing_local_song_id:
            return MANUAL_USER_LINKED_LOCAL_SONG
        if status is ComparisonStatus.FOUND:
            return MANUAL_USER_MARKED_FOUND
        if status is ComparisonStatus.MISSING:
            return MANUAL_USER_MARKED_MISSING
        if status is ComparisonStatus.POSSIBLE_MATCH:
            return MANUAL_USER_MARKED_POSSIBLE
        return MANUAL_USER_LINKED_LOCAL_SONG
