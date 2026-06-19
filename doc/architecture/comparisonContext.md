# Contexto de Comparacion

## Objetivo

Unificar en un solo documento el flujo funcional, tecnico y de persistencia de la comparacion entre playlist de YouTube y biblioteca local.

## Flujo vigente

El flujo activo y canónico es:

1. normalizacion simetrica entre playlist y local
2. filtro duro por titulo comparable
3. filtro duro por artista comparable dentro del subconjunto del titulo
4. exclusion de `local_song` reservadas por `FOUND`
5. score final solo dentro del subconjunto ya validado
6. clasificacion en `FOUND`, `POSSIBLE_MATCH` o `MISSING`
7. persistencia de snapshot de comparacion

## Estados funcionales

### `FOUND`

Se usa cuando:

* titulo y artista ya han quedado validados
* la candidata local es defendible
* no hay ambigüedad irresoluble

Regla dura:

* no puede existir `FOUND` con artista no validado

### `POSSIBLE_MATCH`

Se usa solo cuando:

* titulo y artista ya validaron una o mas candidatas
* el score final no puede romper la ambigüedad de forma segura

No es una salida válida para artistas incorrectos.

### `MISSING`

Se usa cuando:

* no existe titulo en local
* existe titulo pero no artista valido
* tras exclusiones ya no queda candidata util
* no hay base suficiente para una decision defendible

## Score

El score:

* no abre la competicion
* no sustituye filtros duros
* no legitima artistas incorrectos

Solo sirve para:

* evaluar duracion
* confirmar consistencia
* desempatar candidatas validas

## Reserva de canciones locales

Reglas activas:

* una `local_song` en `FOUND` queda reservada
* una `local_song` reservada no vuelve a competir en la misma comparacion
* `POSSIBLE_MATCH` no reserva
* `MISSING` no reserva

Esto reduce ruido y evita duplicar una misma cancion local en dos `FOUND`.

## Snapshot persistido

La comparacion persiste:

### `playlist_comparison`

Cabecera de snapshot con:

* scope de playlist y carpeta local
* marcas temporales de snapshot
* fingerprints de estado
* version de reglas

### `playlist_comparison_result`

Detalle por item con:

* `match_status`
* `local_song_id`
* `score`
* `matched_by`

## Incrementalidad

Reglas activas:

* `FOUND` validos pueden congelarse
* su `local_song_id` queda reservada
* la recomparacion incremental trabaja sobre filas nuevas, `MISSING`, `POSSIBLE_MATCH` y `FOUND` invalidados
* un `FOUND` valido no se reabre solo porque aparezca una candidata aparentemente mejor

## Razones legibles

Razones mínimas esperadas:

* `No existe titulo en local.`
* `Existe titulo en local pero no artista valido.`
* `La cancion local ya esta reservada por otro FOUND.`
* `Varias candidatas comparten titulo y artista; no se puede resolver de forma automatica.`
* `Titulo y artista validos, pero la duracion no permite confirmar FOUND.`
* `Coincidencia confirmada por titulo y artista validos.`

## Aplicacion y UI

### Caso de uso

`CompareYoutubePlaylistWithLocalLibraryUseCase` coordina:

* carga de playlist activa
* carga de biblioteca local activa
* preparacion de comparables
* matching
* persistencia del snapshot
* devolucion de DTOs con resumen, items y observabilidad

### Pantalla de comparacion

La UI debe:

* hidratar snapshot persistido
* permitir `Refrescar snapshot`
* permitir `Recomparar pendientes`
* permitir `Recomparar todo`
* mostrar estado del snapshot
* mostrar motivos legibles
* permitir override manual sobre el snapshot actual

## Regla documental

Este documento sustituye como referencia viva la documentacion fragmentada de comparación.

Si aparece un documento antiguo que contradice este flujo, prevalece este documento.

