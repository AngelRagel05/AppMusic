from __future__ import annotations

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.domain.filters.entities.ignoredTerm import IgnoredTerm

def mapIgnoredTermToDto(ignored_term: IgnoredTerm) -> IgnoredTermDto:
    return IgnoredTermDto(
        id=ignored_term.id or 0,
        term=ignored_term.term,
        scope=ignored_term.scope,
        language=ignored_term.language,
        is_active=ignored_term.is_active,
    )
