# Comparison Candidate Index And Stage Filtering

## Contexto

La comparacion incremental ya congelaba `FOUND` validos, pero para los items restantes seguia pasando un pool demasiado grande al matcher.

Eso mantenia un coste alto en bibliotecas grandes porque muchos items seguian evaluando mas candidatas de las necesarias.

## Decision

Se introduce una colaboracion separada del matcher:

* `ComparableLocalSongCandidateIndex`
* `buildCandidateSelectionBatches(...)`

El matcher no sabe como se construye el indice. Solo recibe la lista de candidatas de cada etapa.

## Indices

La biblioteca local comparable se indexa por:

* `title`
* `artist`
* `title + artist`

## Etapas de seleccion

El `use case` consume el indice en tres etapas:

1. `exact`
   * candidatas por `title + artist` exacto
   * y despues por `title` exacto
2. `very_similar`
   * candidatas con titulo muy parecido segun politica unica de similitud
3. `broad`
   * candidatas por artista exacto
   * y, si hace falta, el resto del pool no reservado

## Reglas operativas

* el pool reservado por `FOUND` validos se excluye en todas las etapas
* si la etapa `exact` devuelve `FOUND`, se corta
* si la etapa `very_similar` devuelve `FOUND`, se corta
* si no, se sigue hasta `broad`
* el fallback amplio mantiene equivalencia funcional en los casos cubiertos

## Consecuencias

* los casos triviales dejan de puntuar toda la biblioteca
* el pool decrece conforme se confirman `FOUND`
* el matcher sigue siendo una pieza pura de decision
* la estrategia de seleccion queda ajustable sin remezclar scoring y construccion de indices
