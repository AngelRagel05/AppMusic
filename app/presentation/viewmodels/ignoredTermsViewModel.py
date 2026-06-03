from __future__ import annotations

from app.application.dto.createIgnoredTermInputDto import CreateIgnoredTermInputDto
from app.application.dto.deleteIgnoredTermInputDto import DeleteIgnoredTermInputDto
from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.updateIgnoredTermInputDto import UpdateIgnoredTermInputDto
from app.application.use_cases.createIgnoredTermUseCase import CreateIgnoredTermUseCase
from app.application.use_cases.deleteIgnoredTermUseCase import DeleteIgnoredTermUseCase
from app.application.use_cases.listIgnoredTermsUseCase import ListIgnoredTermsUseCase
from app.application.use_cases.updateIgnoredTermUseCase import UpdateIgnoredTermUseCase


class IgnoredTermsViewModel:
    def __init__(
        self,
        list_use_case: ListIgnoredTermsUseCase,
        create_use_case: CreateIgnoredTermUseCase,
        update_use_case: UpdateIgnoredTermUseCase,
        delete_use_case: DeleteIgnoredTermUseCase,
    ) -> None:
        self._list_use_case = list_use_case
        self._create_use_case = create_use_case
        self._update_use_case = update_use_case
        self._delete_use_case = delete_use_case

    def load_terms(self) -> list[IgnoredTermDto]:
        return self._list_use_case.execute()

    def create_term(self, term: str, scope: str, language: str) -> IgnoredTermDto:
        return self._create_use_case.execute(
            CreateIgnoredTermInputDto(
                term=term,
                scope=scope,
                language=language,
            )
        )

    def update_term(self, term_id: int, term: str, scope: str, language: str) -> IgnoredTermDto:
        return self._update_use_case.execute(
            UpdateIgnoredTermInputDto(
                term_id=term_id,
                term=term,
                scope=scope,
                language=language,
            )
        )

    def delete_term(self, term_id: int) -> None:
        self._delete_use_case.execute(DeleteIgnoredTermInputDto(term_id=term_id))
