from __future__ import annotations

from app.application.dto.create_ignored_term_input_dto import CreateIgnoredTermInputDto
from app.application.dto.ignored_term_dto import IgnoredTermDto
from app.domain.services.ignored_term_repository import IgnoredTermRepository


class CreateIgnoredTermUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: CreateIgnoredTermInputDto) -> IgnoredTermDto:
        normalized_term = input_dto.term.strip().lower()
        normalized_scope = input_dto.scope.strip().lower()
        normalized_language = input_dto.language.strip().lower()

        if not normalized_term:
            msg = "El termino no puede estar vacio."
            raise ValueError(msg)

        if not normalized_scope:
            msg = "El scope no puede estar vacio."
            raise ValueError(msg)

        if not normalized_language:
            msg = "El idioma no puede estar vacio."
            raise ValueError(msg)

        ignored_term = self._repository.create(
            term=normalized_term,
            scope=normalized_scope,
            language=normalized_language,
        )
        return IgnoredTermDto(
            id=ignored_term.id or 0,
            term=ignored_term.term,
            scope=ignored_term.scope,
            language=ignored_term.language,
            is_active=ignored_term.is_active,
        )
