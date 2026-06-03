from __future__ import annotations

from app.application.dto.createIgnoredTermInputDto import CreateIgnoredTermInputDto
from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.ignoredTermSupport import (
    mapIgnoredTermToDto,
    normalizeIgnoredTermData,
)
from app.domain.repositories.ignoredTermRepository import IgnoredTermRepository


class CreateIgnoredTermUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: CreateIgnoredTermInputDto) -> IgnoredTermDto:
        normalized_data = normalizeIgnoredTermData(
            term=input_dto.term,
            scope=input_dto.scope,
            language=input_dto.language,
        )

        ignored_term = self._repository.create(
            term=normalized_data.term,
            scope=normalized_data.scope,
            language=normalized_data.language,
        )
        return mapIgnoredTermToDto(ignored_term)
