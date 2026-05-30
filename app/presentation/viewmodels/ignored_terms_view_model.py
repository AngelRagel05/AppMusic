from __future__ import annotations

from app.application.dto.create_ignored_term_input_dto import CreateIgnoredTermInputDto
from app.application.dto.ignored_term_dto import IgnoredTermDto
from app.application.use_cases.create_ignored_term_use_case import CreateIgnoredTermUseCase
from app.application.use_cases.list_ignored_terms_use_case import ListIgnoredTermsUseCase


class IgnoredTermsViewModel:
    def __init__(
        self,
        list_use_case: ListIgnoredTermsUseCase,
        create_use_case: CreateIgnoredTermUseCase,
    ) -> None:
        self._list_use_case = list_use_case
        self._create_use_case = create_use_case

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
