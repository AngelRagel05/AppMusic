from __future__ import annotations

from app.application.dto.pagedLocalSongsDto import PagedLocalSongsDto
from app.application.use_cases.metadata.localSongMapping import mapLocalSongToDto
from app.domain.library.entities.localSong import LocalSong
from app.domain.library.repositories.localSongRepository import LocalSongRepository


class ListLocalSongsUseCase:
    _SORTERS = {
        "title": lambda song: (song.title.casefold(), song.file_name.casefold()),
        "artist": lambda song: (song.artist.casefold(), song.title.casefold()),
        "album": lambda song: (song.album.casefold(), song.title.casefold()),
        "year": lambda song: (song.release_year, song.title.casefold()),
        "fileName": lambda song: song.file_name.casefold(),
    }

    def __init__(self, repository: LocalSongRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        local_folder_id: int,
        search: str = "",
        availability: str = "all",
        sort_by: str = "title",
        sort_direction: str = "asc",
        page: int = 1,
        page_size: int = 25,
    ) -> PagedLocalSongsDto:
        if local_folder_id <= 0:
            raise ValueError("La biblioteca seleccionada no es valida.")
        if page <= 0 or page_size <= 0:
            raise ValueError("La paginacion debe usar valores positivos.")
        if availability not in {"all", "available", "missing"}:
            raise ValueError("El filtro de disponibilidad no es valido.")
        sorter = self._SORTERS.get(sort_by)
        if sorter is None:
            raise ValueError("El criterio de ordenacion no es valido.")
        if sort_direction not in {"asc", "desc"}:
            raise ValueError("La direccion de ordenacion no es valida.")

        songs = self._repository.list_by_folder(local_folder_id)
        normalized_search = search.strip().casefold()
        filtered_songs = [
            song
            for song in songs
            if self._matchesSearch(song, normalized_search)
            and self._matchesAvailability(song, availability)
        ]
        filtered_songs.sort(
            key=sorter,
            reverse=sort_direction == "desc",
        )
        start = (page - 1) * page_size
        return PagedLocalSongsDto(
            items=[
                mapLocalSongToDto(song)
                for song in filtered_songs[start : start + page_size]
            ],
            total=len(filtered_songs),
            page=page,
            page_size=page_size,
        )

    def _matchesSearch(self, song: LocalSong, search: str) -> bool:
        if not search:
            return True
        return any(
            search in value.casefold()
            for value in (
                song.title,
                song.artist,
                song.album,
                song.file_name,
            )
        )

    def _matchesAvailability(self, song: LocalSong, availability: str) -> bool:
        if availability == "all":
            return True
        if availability == "available":
            return song.is_available
        return not song.is_available
