from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from app.infrastructure.filesystem import LocalMusicScanner


def test_scanMp3Files_returns_absolute_mp3_paths_recursively(tmp_path: Path) -> None:
    scanner = LocalMusicScanner()
    musicFolder = tmp_path / "music"
    albumFolder = musicFolder / "album"
    albumFolder.mkdir(parents=True)
    rootSong = musicFolder / "track01.mp3"
    nestedSong = albumFolder / "track02.MP3"
    ignoredFile = albumFolder / "cover.jpg"
    rootSong.write_text("fake mp3", encoding="utf-8")
    nestedSong.write_text("fake mp3", encoding="utf-8")
    ignoredFile.write_text("fake image", encoding="utf-8")

    discoveredFiles = scanner.scanMp3Files(str(musicFolder))

    assert discoveredFiles == sorted(
        [str(rootSong.resolve()), str(nestedSong.resolve())],
        key=str.casefold,
    )


def test_scanMp3Files_raises_file_not_found_when_folder_does_not_exist(tmp_path: Path) -> None:
    scanner = LocalMusicScanner()

    try:
        scanner.scanMp3Files(str(tmp_path / "missing"))
    except FileNotFoundError as error:
        assert str(error) == str(tmp_path / "missing")
    else:
        raise AssertionError("Se esperaba FileNotFoundError cuando la carpeta no existe.")


def test_scanMp3Files_returns_empty_list_when_folder_has_no_mp3_files(tmp_path: Path) -> None:
    scanner = LocalMusicScanner()
    musicFolder = tmp_path / "music"
    musicFolder.mkdir()
    (musicFolder / "cover.jpg").write_text("fake image", encoding="utf-8")
    (musicFolder / "notes.txt").write_text("fake text", encoding="utf-8")

    discoveredFiles = scanner.scanMp3Files(str(musicFolder))

    assert discoveredFiles == []


def test_scanMp3Files_ignores_non_mp3_files_even_when_names_are_similar(tmp_path: Path) -> None:
    scanner = LocalMusicScanner()
    musicFolder = tmp_path / "music"
    musicFolder.mkdir()
    validSong = musicFolder / "track.mp3"
    almostMp3 = musicFolder / "track.mp34"
    noExtension = musicFolder / "trackmp3"
    validSong.write_text("fake mp3", encoding="utf-8")
    almostMp3.write_text("fake file", encoding="utf-8")
    noExtension.write_text("fake file", encoding="utf-8")

    discoveredFiles = scanner.scanMp3Files(str(musicFolder))

    assert discoveredFiles == [str(validSong.resolve())]


def test_scanMp3Files_raises_permission_error_when_root_folder_cannot_be_read(tmp_path: Path) -> None:
    scanner = LocalMusicScanner()
    musicFolder = tmp_path / "music"
    musicFolder.mkdir()

    with patch("app.infrastructure.filesystem.localMusicScanner.Path.iterdir", side_effect=PermissionError("denied")):
        try:
            scanner.scanMp3Files(str(musicFolder))
        except PermissionError as error:
            assert str(error) == str(musicFolder)
        else:
            raise AssertionError("Se esperaba PermissionError cuando la carpeta no puede leerse.")
