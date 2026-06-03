from __future__ import annotations

import pytest
from app.application.dto.createIgnoredTermInputDto import CreateIgnoredTermInputDto
from app.application.dto.deleteIgnoredTermInputDto import DeleteIgnoredTermInputDto
from app.application.dto.updateIgnoredTermInputDto import UpdateIgnoredTermInputDto
from app.application.use_cases.createIgnoredTermUseCase import CreateIgnoredTermUseCase
from app.application.use_cases.deleteIgnoredTermUseCase import DeleteIgnoredTermUseCase
from app.application.use_cases.listIgnoredTermsUseCase import ListIgnoredTermsUseCase
from app.application.use_cases.updateIgnoredTermUseCase import UpdateIgnoredTermUseCase
from app.domain.entities.ignoredTerm import IgnoredTerm
from app.domain.repositories.ignoredTermRepository import IgnoredTermRepository


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

    def update(self, term_id: int, term: str, scope: str, language: str) -> IgnoredTerm:
        for index, ignored_term in enumerate(self._terms):
            if ignored_term.id == term_id:
                updated_term = IgnoredTerm(
                    id=ignored_term.id,
                    term=term,
                    scope=scope,
                    language=language,
                    is_active=ignored_term.is_active,
                )
                self._terms[index] = updated_term
                return updated_term

        msg = "El termino ignorado seleccionado no existe."
        raise ValueError(msg)

    def delete(self, term_id: int) -> None:
        for index, ignored_term in enumerate(self._terms):
            if ignored_term.id == term_id:
                del self._terms[index]
                return

        msg = "El termino ignorado seleccionado no existe."
        raise ValueError(msg)


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


def test_update_ignored_term_use_case_updates_values() -> None:
    repository = InMemoryIgnoredTermRepository()
    created_term = repository.create("audio", "title", "global")
    use_case = UpdateIgnoredTermUseCase(repository)

    ignored_term = use_case.execute(
        UpdateIgnoredTermInputDto(
            term_id=created_term.id or 0,
            term="  official ",
            scope=" artist ",
            language=" en ",
        )
    )

    assert ignored_term.term == "official"
    assert ignored_term.scope == "artist"
    assert ignored_term.language == "en"


def test_delete_ignored_term_use_case_removes_term() -> None:
    repository = InMemoryIgnoredTermRepository()
    created_term = repository.create("audio", "title", "global")
    use_case = DeleteIgnoredTermUseCase(repository)

    use_case.execute(DeleteIgnoredTermInputDto(term_id=created_term.id or 0))

    assert repository.list_all() == []
