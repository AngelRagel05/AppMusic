# Playlist Comparison Result Model

## Contexto

La comparacion entre items importados de YouTube y canciones locales necesita un modelo explicito antes de implementar el matching.

Sin ese contrato previo, la logica de comparacion y la UI quedarían acopladas a estructuras improvisadas.

## Decision

La Fase 1 define dos DTOs de aplicacion y un estado compartido:

* `PlaylistComparisonItemResultDto`
* `PlaylistComparisonSummaryDto`
* `ComparisonStatus`

`ComparisonStatus` queda en `app/shared/constants/` con tres valores:

* `found`
* `missing`
* `possible_match`

`PlaylistComparisonItemResultDto` representa el resultado por item comparado y separa:

* identificadores
* estado de comparacion
* datos visibles de YouTube
* datos visibles de la cancion local candidata
* score
* razon textual

`PlaylistComparisonSummaryDto` concentra los contadores agregados del proceso.

## Consecuencias

* el caso de uso de comparacion ya tiene un contrato de salida claro
* la UI puede pintar estados y resúmenes sin depender todavía del algoritmo
* el matching podrá evolucionar sin romper la forma del resultado
