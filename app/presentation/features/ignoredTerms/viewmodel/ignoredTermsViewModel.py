from __future__ import annotations

from app.application.dto.createIgnoredTermInputDto import CreateIgnoredTermInputDto
from app.application.dto.deleteIgnoredTermInputDto import DeleteIgnoredTermInputDto
from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.application.dto.updateIgnoredTermInputDto import UpdateIgnoredTermInputDto
from app.application.use_cases import (
    CreateIgnoredTermUseCase,
    DeleteIgnoredTermUseCase,
    ListIgnoredTermsUseCase,
    UpdateIgnoredTermUseCase,
)


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
        self._terms_cache: list[IgnoredTermDto] = []
        self._terms_by_id: dict[int, IgnoredTermDto] = {}

    def refreshState(self) -> list[IgnoredTermDto]:
        ignoredTerms = self._list_use_case.execute()
        self._storeTerms(ignoredTerms)
        return ignoredTerms

    def load_terms(self) -> list[IgnoredTermDto]:
        if not self._terms_cache:
            self.refreshState()
        return list(self._terms_cache)

    def find_term_by_id(self, term_id: int) -> IgnoredTermDto | None:
        if not self._terms_cache:
            self.refreshState()
        return self._terms_by_id.get(term_id)

    def create_term(self, term: str, scope: str, language: str) -> IgnoredTermDto:
        ignoredTerm = self._create_use_case.execute(
            CreateIgnoredTermInputDto(
                term=term,
                scope=scope,
                language=language,
            )
        )
        self.refreshState()
        return ignoredTerm

    def update_term(self, term_id: int, term: str, scope: str, language: str) -> IgnoredTermDto:
        ignoredTerm = self._update_use_case.execute(
            UpdateIgnoredTermInputDto(
                term_id=term_id,
                term=term,
                scope=scope,
                language=language,
            )
        )
        self.refreshState()
        return ignoredTerm

    def delete_term(self, term_id: int) -> None:
        self._delete_use_case.execute(DeleteIgnoredTermInputDto(term_id=term_id))
        self.refreshState()

    def _storeTerms(self, ignoredTerms: list[IgnoredTermDto]) -> None:
        self._terms_cache = list(ignoredTerms)
        self._terms_by_id = {term.id: term for term in ignoredTerms}
