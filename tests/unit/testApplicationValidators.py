from __future__ import annotations

import pytest

from app.application.validators.filters.ignoredTermValidators import (
    normalizeIgnoredTermData,
    validateIgnoredTermId,
)
from app.application.validators.library.localFolderValidators import (
    normalizeLocalFolderData,
    validateLocalFolderId,
)
from app.application.validators.playlists.youtubePlaylistValidators import (
    normalizeYoutubePlaylistData,
    validateYoutubePlaylistId,
)
from app.shared.exceptions import ValidationError


def test_normalize_local_folder_data_resolves_existing_folder(tmp_path) -> None:
    normalized_data = normalizeLocalFolderData(f"  {tmp_path}  ")

    assert normalized_data.path == str(tmp_path.resolve())
    assert normalized_data.display_name == tmp_path.name


def test_validate_local_folder_id_rejects_non_positive_values() -> None:
    with pytest.raises(ValidationError, match="biblioteca seleccionada"):
        validateLocalFolderId(0)


def test_normalize_youtube_playlist_data_builds_canonical_url() -> None:
    normalized_data = normalizeYoutubePlaylistData(
        playlist_url="  https://music.youtube.com/playlist?list=PL123  ",
        title="  Favoritas  ",
    )

    assert normalized_data.playlist_url == "https://www.youtube.com/playlist?list=PL123"
    assert normalized_data.external_playlist_id == "PL123"
    assert normalized_data.title == "Favoritas"


def test_validate_youtube_playlist_id_rejects_non_positive_values() -> None:
    with pytest.raises(ValidationError, match="playlist seleccionada"):
        validateYoutubePlaylistId(0)


def test_normalize_ignored_term_data_trims_and_lowercases_values() -> None:
    normalized_data = normalizeIgnoredTermData(
        term="  LIVE  ",
        scope=" Title ",
        language=" Global ",
    )

    assert normalized_data.term == "live"
    assert normalized_data.scope == "title"
    assert normalized_data.language == "global"


def test_validate_ignored_term_id_rejects_non_positive_values() -> None:
    with pytest.raises(ValidationError, match="identificador"):
        validateIgnoredTermId(0)
