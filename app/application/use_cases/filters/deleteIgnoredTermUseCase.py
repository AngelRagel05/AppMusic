from __future__ import annotations

from app.application.dto.deleteIgnoredTermInputDto import DeleteIgnoredTermInputDto
from app.application.validators.filters.ignoredTermValidators import (
    validateIgnoredTermId,
)
from app.domain.filters.repositories.ignoredTermRepository import IgnoredTermRepository


class DeleteIgnoredTermUseCase:
    def __init__(self, repository: IgnoredTermRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: DeleteIgnoredTermInputDto) -> None:
        validateIgnoredTermId(input_dto.term_id)
        self._repository.delete(input_dto.term_id)
