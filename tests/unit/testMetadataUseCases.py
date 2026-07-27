from __future__ import annotations

from app.application.dto.localSongMetadataDto import LocalSongMetadataDto
from app.application.dto.localSongMetadataUpdateDto import LocalSongMetadataUpdateDto
from app.application.use_cases.metadata import UpdateLocalSongMetadataUseCase
from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.entities.localSong import LocalSong


class LocalSongRepositorySpy:
    def __init__(self, song: LocalSong) -> None:
        self.song = song
        self.saved_song: LocalSong | None = None

    def get_by_id(self, local_song_id: int) -> LocalSong | None:
        return self.song if local_song_id == self.song.id else None

    def save(self, song: LocalSong) -> LocalSong:
        self.saved_song = song
        return song


class LocalFolderRepositorySpy:
    def __init__(self, folder: LocalFolder) -> None:
        self.folder = folder

    def list_all(self) -> list[LocalFolder]:
        return [self.folder]


class MetadataWriterSpy:
    def __init__(self) -> None:
        self.calls: list[tuple[str, LocalSongMetadataUpdateDto]] = []

    def writeMetadata(
        self,
        filePath: str,
        metadata: LocalSongMetadataUpdateDto,
    ) -> None:
        self.calls.append((filePath, metadata))


class MetadataReaderStub:
    def readMetadata(self, _filePath: str) -> LocalSongMetadataDto:
        return LocalSongMetadataDto(
            title="Titulo verificado",
            artist="Artista verificado",
            album="Album",
            release_year=2026,
            track_number_album=2,
            duration_seconds=180.5,
        )


def test_update_metadata_writes_rereads_and_only_then_updates_index(tmp_path) -> None:
    folder_path = tmp_path / "library"
    folder_path.mkdir()
    song_path = folder_path / "song.mp3"
    song_path.write_bytes(b"test")
    song = LocalSong(
        id=7,
        local_folder_id=3,
        file_path=str(song_path),
        file_name=song_path.name,
        title="Anterior",
        duration_seconds=180.5,
    )
    song_repository = LocalSongRepositorySpy(song)
    writer = MetadataWriterSpy()
    use_case = UpdateLocalSongMetadataUseCase(
        song_repository,
        LocalFolderRepositorySpy(
            LocalFolder(
                id=3,
                path=str(folder_path),
                display_name="Library",
                is_active=True,
            )
        ),
        writer,
        MetadataReaderStub(),
    )

    result = use_case.execute(
        7,
        LocalSongMetadataUpdateDto(
            title="Titulo pedido",
            artist="Artista pedido",
            album="Album",
            release_year=2026,
            track_number_album=2,
        ),
    )

    assert writer.calls[0][0] == str(song_path)
    assert result.title == "Titulo verificado"
    assert result.artist == "Artista verificado"
    assert song_repository.saved_song is not None
    assert song_repository.saved_song.normalized_title == "titulo verificado"


def test_update_metadata_rejects_file_outside_registered_library(tmp_path) -> None:
    library_path = tmp_path / "library"
    library_path.mkdir()
    outside_song = tmp_path / "outside.mp3"
    outside_song.write_bytes(b"test")
    use_case = UpdateLocalSongMetadataUseCase(
        LocalSongRepositorySpy(
            LocalSong(
                id=7,
                local_folder_id=3,
                file_path=str(outside_song),
                file_name=outside_song.name,
            )
        ),
        LocalFolderRepositorySpy(
            LocalFolder(
                id=3,
                path=str(library_path),
                display_name="Library",
                is_active=True,
            )
        ),
        MetadataWriterSpy(),
        MetadataReaderStub(),
    )

    try:
        use_case.execute(
            7,
            LocalSongMetadataUpdateDto("Title", "", "", 0, 0),
        )
    except ValueError as error:
        assert "fuera de la biblioteca" in str(error)
    else:
        raise AssertionError("Se esperaba el rechazo de la ruta no autorizada.")
