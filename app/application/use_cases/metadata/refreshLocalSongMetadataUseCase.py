from app.application.dto.localSongDto import LocalSongDto
from app.application.dto.localSongMetadataUpdateDto import LocalSongMetadataUpdateDto
from app.application.use_cases.metadata.localSongMapping import mapLocalSongToDto
from app.application.use_cases.metadata.updateLocalSongMetadataUseCase import (
    LocalSongMetadataReaderPort,
    LocalSongMetadataWriterPort,
    UpdateLocalSongMetadataUseCase,
)
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.domain.library.repositories.localSongRepository import LocalSongRepository


class _NoOpMetadataWriter(LocalSongMetadataWriterPort):
    def writeMetadata(
        self,
        filePath: str,
        metadata: LocalSongMetadataUpdateDto,
    ) -> None:
        return None


class RefreshLocalSongMetadataUseCase(UpdateLocalSongMetadataUseCase):
    def __init__(
        self,
        local_song_repository: LocalSongRepository,
        local_folder_repository: LocalFolderRepository,
        metadata_reader: LocalSongMetadataReaderPort,
    ) -> None:
        super().__init__(
            local_song_repository,
            local_folder_repository,
            _NoOpMetadataWriter(),
            metadata_reader,
        )
        self._metadata_reader = metadata_reader

    def execute(self, local_song_id: int) -> LocalSongDto:
        local_song = self._getValidatedLocalSong(local_song_id)
        persisted_metadata = self._metadata_reader.readMetadata(local_song.file_path)
        updated_song = self._local_song_repository.save(
            self._mergeMetadata(local_song, persisted_metadata)
        )
        return mapLocalSongToDto(updated_song)
