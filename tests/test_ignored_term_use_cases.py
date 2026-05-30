from __future__ import annotations

import pytest
from app.application.dto.create_ignored_term_input_dto import CreateIgnoredTermInputDto
from app.application.use_cases.create_ignored_term_use_case import CreateIgnoredTermUseCase
from app.application.use_cases.list_ignored_terms_use_case import ListIgnoredTermsUseCase
from app.domain.entities.ignored_term import IgnoredTerm
from app.domain.services.ignored_term_repository import IgnoredTermRepository


class InMemoryIgnoredTermRepository(IgnoredTermRepository):
    def __init__(self) -> None:
        self._terms: list[IgnoredTerm] = []
        self._next_id = 1

    def list_all(self) -> list[IgnoredTerm]:
        return list(self._terms)

    def create(self, term: str, scope: str, language: str) -> IgnoredTerm:
        ignored_term = IgnoredTerm(
            id=self._next_id,
            term=term,
            scope=scope,
            language=language,
            is_active=True,
        )
        self._terms.append(ignored_term)
        self._next_id += 1
        return ignored_term


def test_list_ignored_terms_use_case_maps_entities_to_dto() -> None:
    repository = InMemoryIgnoredTermRepository()
    repository.create("audio", "title", "global")
    use_case = ListIgnoredTermsUseCase(repository)

    ignored_terms = use_case.execute()

    assert ignored_terms[0].term == "audio"
    assert ignored_terms[0].scope == "title"


def test_create_ignored_term_use_case_normalizes_values() -> None:
    repository = InMemoryIgnoredTermRepository()
    use_case = CreateIgnoredTermUseCase(repository)

    ignored_term = use_case.execute(
        CreateIgnoredTermInputDto(
            term="  LIVE  ",
            scope="  TITLE ",
            language=" Global ",
        )
    )

    assert ignored_term.term == "live"
    assert ignored_term.scope == "title"
    assert ignored_term.language == "global"


def test_create_ignored_term_use_case_rejects_empty_term() -> None:
    repository = InMemoryIgnoredTermRepository()
    use_case = CreateIgnoredTermUseCase(repository)

    with pytest.raises(ValueError, match="termino"):
        use_case.execute(
            CreateIgnoredTermInputDto(
                term="   ",
                scope="title",
                language="global",
            )
        )
