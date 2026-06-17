# Comparison Observability And Performance Validation

## Contexto

La comparacion ya era incremental, pero faltaba medir con precision donde se consume el tiempo y cuanto trabajo real evita cada recomparacion.

Sin observabilidad, no hay forma fiable de validar:

* si `refresh` sigue siendo barato
* si `recomparar pendientes` reduce coste de verdad
* si una optimizacion cambia tiempos sin degradar resultados

## Decision

`CompareYoutubePlaylistWithLocalLibraryUseCase` expone observabilidad estructurada en `PlaylistComparisonResultDto.observability`.

La observabilidad se divide en dos bloques:

### Tiempos por fase

* `snapshot_load_seconds`
* `pool_build_seconds`
* `indexing_seconds`
* `matching_seconds`
* `persistence_seconds`
* `total_seconds`

### Metricas de volumen

* `skipped_found_count`
* `reserved_local_song_count`
* `recomputed_item_count`
* `total_candidates_considered`
* `average_candidates_per_recomputed_item`

## Reglas

* `LoadPersistedPlaylistComparisonUseCase` no genera estas metricas porque solo rehidrata snapshot
* la observabilidad se calcula en el use case de recomparacion, no en UI
* el promedio de candidatas se mide sobre candidatas unicas realmente evaluadas por item recomparado
* un `FOUND` congelado cuenta como `skipped_found_count`
* las canciones ya reservadas por esos `FOUND` cuentan como `reserved_local_song_count`

## Validacion operativa

Para comparar antes y despues con datos reales:

1. ejecutar una recomparacion completa y guardar `observability.phase_timings.total_seconds`
2. ejecutar una recomparacion incremental equivalente y guardar el mismo dato
3. comparar tambien:
   * `summary.found_count`
   * `summary.possible_match_count`
   * `summary.missing_count`
   * `volume_metrics.recomputed_item_count`
   * `volume_metrics.average_candidates_per_recomputed_item`

## Regresiones minimas a mantener

* caso `NADAL 015 #MEMORIES I`
* casos ambiguos con dos candidatas plausibles
* casos con titulo competitivo pero artista inconsistente

## Consecuencias

* el beneficio de cada fase incremental queda medible sin acoplarse a la interfaz
* la validacion de rendimiento deja de depender de impresiones manuales
* los cambios futuros en indice, corte temprano o invalidacion pueden revisarse con datos comparables
