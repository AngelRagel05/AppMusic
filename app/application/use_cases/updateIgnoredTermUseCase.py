from __future__ import annotations

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.updateIgnoredTermInputDto import UpdateIgnoredTermInputDto
from app.application.ignoredTermSupport import (
    mapIgnoredTermToDto,
    normalizeIgnoredTermData,
    validateIgnoredTermId,
)
from app.domain.repositories.ignoredTermRepository import IgnoredTermRepository


class UpdateIgnoredTermUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: UpdateIgnoredTermInputDto) -> IgnoredTermDto:
        validateIgnoredTermId(input_dto.term_id)
        normalized_data = normalizeIgnoredTermData(
            term=input_dto.term,
            scope=input_dto.scope,
            language=input_dto.language,
        )

        ignored_term = self._repository.update(
            term_id=input_dto.term_id,
            term=normalized_data.term,
            scope=normalized_data.scope,
            language=normalized_data.language,
        )
        return mapIgnoredTermToDto(ignored_term)
