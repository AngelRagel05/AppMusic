from __future__ import annotations

from app.application.dto.ignored_term_dto import IgnoredTermDto
from app.domain.services.ignored_term_repository import IgnoredTermRepository


class ListIgnoredTermsUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self) -> list[IgnoredTermDto]:
        ignored_terms = self._repository.list_all()
        return [
            IgnoredTermDto(
                id=ignored_term.id or 0,
                term=ignored_term.term,
                scope=ignored_term.scope,
                language=ignored_term.language,
                is_active=ignored_term.is_active,
            )
            for ignored_term in ignored_terms
        ]
