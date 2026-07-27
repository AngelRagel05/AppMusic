from app.application.dto.localSongDto import LocalSongDto
from app.domain.library.entities.localSong import LocalSong


def mapLocalSongToDto(local_song: LocalSong) -> LocalSongDto:
    return LocalSongDto(
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
