# Matcher Early Cutoff Policy

## Contexto

La comparacion persistida ya evita gran parte del trabajo al congelar `FOUND` validos, pero el matcher seguia puntuando todas las candidatas restantes aunque existiera una coincidencia claramente dominante.

## Decision

Se introduce una politica unica de corte temprano dentro de `persistedPlaylistItemMatcherService`.

El corte temprano solo se permite si se cumplen todas estas condiciones:

* el artista ya ha sido validado como `STRONG`
* el titulo tiene evidencia `EXACT` o `NEAR_EXACT`
* la similitud normalizada del titulo es `>= 0.93`
* dentro del pool actual solo existe una candidata que cumpla esa politica

## Reglas negativas

No se corta si:

* el artista es `MEDIUM`, `WEAK` o `NONE`
* el titulo es solo `CONTAINS` o `WEAK`
* existe mas de una candidata que pase la politica y pueda haber empate real

## Consecuencias

* la heuristica de corte queda centralizada y ajustable desde una sola politica
* el matcher no deja de validar el artista antes de cortar
* el corte no se aplica fuera del matcher ni disperso por otros use cases
