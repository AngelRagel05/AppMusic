from __future__ import annotations

import pytest

from app.application.ignoredTermSupport import mapIgnoredTermToDto
from app.application.validators.filters.ignoredTermValidators import (
    normalizeIgnoredTermData,
    validateIgnoredTermId,
)
from app.domain.filters.entities.ignoredTerm import IgnoredTerm


def test_normalize_ignored_term_data_trims_and_lowercases_values() -> None:
    normalized = normalizeIgnoredTermData(
        term="  LIVE  ",
        scope=" Title ",
        language=" Global ",
    )

    assert normalized.term == "live"
    assert normalized.scope == "title"
    assert normalized.language == "global"


def test_validate_ignored_term_id_rejects_non_positive_values() -> None:
    with pytest.raises(ValueError, match="identificador"):
        validateIgnoredTermId(0)


def test_map_ignored_term_to_dto_preserves_entity_values() -> None:
    ignored_term = IgnoredTerm(
        id=7,
        term="official",
        scope="artist",
        language="en",
        is_active=True,
    )

    dto = mapIgnoredTermToDto(ignored_term)

    assert dto.id == 7
    assert dto.term == "official"
    assert dto.scope == "artist"
    assert dto.language == "en"
    assert dto.is_active is True
