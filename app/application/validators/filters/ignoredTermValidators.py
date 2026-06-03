from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedIgnoredTermData:
    term: str
    scope: str
    language: str


def validateIgnoredTermId(term_id: int) -> None:
    if term_id <= 0:
        msg = "El identificador del termino ignorado no es valido."
        raise ValueError(msg)


def normalizeIgnoredTermData(
    term: str,
    scope: str,
    language: str,
) -> NormalizedIgnoredTermData:
    normalized_term = term.strip().lower()
    if not normalized_term:
        msg = "El termino ignorado no puede estar vacio."
        raise ValueError(msg)

    normalized_scope = scope.strip().lower()
    if not normalized_scope:
        msg = "El ambito del termino ignorado no puede estar vacio."
        raise ValueError(msg)

    normalized_language = language.strip().lower()
    if not normalized_language:
        msg = "El idioma del termino ignorado no puede estar vacio."
        raise ValueError(msg)

    return NormalizedIgnoredTermData(
        term=normalized_term,
        scope=normalized_scope,
        language=normalized_language,
    )
