from __future__ import annotations

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.ignoredTermSupport import mapIgnoredTermToDto
from app.domain.repositories.ignoredTermRepository import IgnoredTermRepository


class ListIgnoredTermsUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self) -> list[IgnoredTermDto]:
        ignored_terms = self._repository.list_all()
        return [mapIgnoredTermToDto(ignored_term) for ignored_term in ignored_terms]
