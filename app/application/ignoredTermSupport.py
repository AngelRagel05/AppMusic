from __future__ import annotations

from dataclasses import dataclass

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.domain.entities.ignoredTerm import IgnoredTerm


@dataclass(frozen=True, slots=True)
class NormalizedIgnoredTermData:
    term: str
    scope: str
    language: str


def validateIgnoredTermId(term_id: int) -> None:
    if term_id <= 0:
        msg = "El identificador del termino no es valido."
        raise ValueError(msg)


def normalizeIgnoredTermData(term: str, scope: str, language: str) -> NormalizedIgnoredTermData:
    normalized_term = term.strip().lower()
    normalized_scope = scope.strip().lower()
    normalized_language = language.strip().lower()

    if not normalized_term:
        msg = "El termino no puede estar vacio."
        raise ValueError(msg)

    if not normalized_scope:
        msg = "El scope no puede estar vacio."
        raise ValueError(msg)

    if not normalized_language:
        msg = "El idioma no puede estar vacio."
        raise ValueError(msg)

    return NormalizedIgnoredTermData(
        term=normalized_term,
        scope=normalized_scope,
        language=normalized_language,
    )


def mapIgnoredTermToDto(ignored_term: IgnoredTerm) -> IgnoredTermDto:
    return IgnoredTermDto(
        id=ignored_term.id or 0,
        term=ignored_term.term,
        scope=ignored_term.scope,
        language=ignored_term.language,
        is_active=ignored_term.is_active,
    )
