from __future__ import annotations

from app.application.dto.localSongDto import LocalSongDto
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository


class ListActiveLocalSongsUseCase:
    def __init__(
        self,
        local_folder_repository: LocalFolderRepository,
        local_song_repository: LocalSongRepository,
    ) -> None:
        self._local_folder_repository = local_folder_repository
        self._local_song_repository = local_song_repository

    def execute(self) -> list[LocalSongDto]:
        active_local_folder = self._local_folder_repository.get_active()
        if active_local_folder is None or active_local_folder.id is None:
            return []

        return [
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
