from __future__ import annotations

from app.infrastructure.database.base import Base
from sqlalchemy import CheckConstraint, UniqueConstraint


def test_metadata_contains_expected_tables() -> None:
    expected_tables = {
        "download",
        "ignored_term",
        "local_folder",
        "local_song",
        "playlist_comparison",
        "playlist_comparison_result",
        "youtube_playlist",
        "youtube_playlist_item",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_playlist_comparison_result_has_unique_constraint_for_comparison_item() -> None:
    table = Base.metadata.tables["playlist_comparison_result"]
    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("playlist_comparison_id", "youtube_playlist_item_id") in unique_constraints


def test_ignored_term_has_composite_unique_constraint() -> None:
    table = Base.metadata.tables["ignored_term"]
    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("term", "scope", "language") in unique_constraints


def test_local_folder_has_unique_constraint_for_path() -> None:
    table = Base.metadata.tables["local_folder"]
    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("path",) in unique_constraints


def test_youtube_playlist_has_unique_constraints_for_url_and_external_id() -> None:
    table = Base.metadata.tables["youtube_playlist"]
    unique_constraints = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("playlist_url",) in unique_constraints
    assert ("external_playlist_id",) in unique_constraints


def test_local_song_has_non_negative_check_constraints() -> None:
    table = Base.metadata.tables["local_song"]
    check_constraints = {
        str(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "track_number_album >= 0" in check_constraints
    assert "duration_seconds >= 0" in check_constraints
