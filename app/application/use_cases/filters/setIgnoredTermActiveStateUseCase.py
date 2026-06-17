from __future__ import annotations

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.setIgnoredTermActiveStateInputDto import (
    SetIgnoredTermActiveStateInputDto,
)
from app.application.ignoredTermSupport import mapIgnoredTermToDto
from app.application.validators.filters.ignoredTermValidators import (
    validateIgnoredTermId,
)
from app.domain.filters.repositories.ignoredTermRepository import IgnoredTermRepository


class SetIgnoredTermActiveStateUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: SetIgnoredTermActiveStateInputDto) -> IgnoredTermDto:
        validateIgnoredTermId(input_dto.term_id)
        ignored_term = self._repository.set_active_state(
            term_id=input_dto.term_id,
            is_active=input_dto.is_active,
        )
        return mapIgnoredTermToDto(ignored_term)
