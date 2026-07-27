from app.application.dto.localSongDto import LocalSongDto
from app.application.use_cases.metadata.localSongMapping import mapLocalSongToDto
from app.domain.library.repositories.localSongRepository import LocalSongRepository


class GetLocalSongUseCase:
    def __init__(self, repository: LocalSongRepository) -> None:
        self._repository = repository

    def execute(self, local_song_id: int) -> LocalSongDto:
        if local_song_id <= 0:
            raise ValueError("El id de la cancion local no es valido.")
        local_song = self._repository.get_by_id(local_song_id)
        if local_song is None:
            raise ValueError("La cancion local seleccionada no existe.")
        return mapLocalSongToDto(local_song)
