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

Queda retirado del flujo activo cualquier esquema por lotes o amplitud progresiva.

Ya no forman parte del comportamiento vigente:

* seleccion por etapas `EXACT`, `VERY_SIMILAR`, `BROAD`
* competicion de candidatas solo por similitud de titulo
* entrada de candidatas con artista no validado al score final
* posibilidad de llegar a `POSSIBLE_MATCH` por titulo y duracion sin validar antes el artista

## Modelo comparable rediseñado

La Fase 2 elimina la asimetria funcional actual entre:

* playlist con comparables ya normalizados
* biblioteca local aun expuesta al matcher mediante `title` y `artist`

El matcher debe trabajar sobre un contrato comparable homogéneo.

### Contrato objetivo

`ComparableYoutubePlaylistItem` debe exponer:

* `id`
* `comparable_title`
* `comparable_artist`
* `duration_seconds`

`ComparableLocalSong` debe exponer:

* `id`
* `comparable_title`
* `comparable_artist`
* `duration_seconds`
* `is_available`
* `is_reserved` cuando la orquestacion lo necesite

La comparacion deja de usar `title` y `artist` como superficie funcional del contrato comparable.

### Decision de persistencia

Se decide persistir campos comparables tambien en `local_song`.

Motivos:

* evita recalcular la normalizacion completa en cada matching
* alinea playlist y biblioteca local bajo el mismo contrato de datos comparables
* permite que fingerprints, snapshots e incrementalidad describan exactamente los valores comparables usados por el matcher
* deja la preparacion de comparables en scan/import y no dentro del matcher

La fase de preparacion sigue existiendo, pero ya no como transformacion efimera en memoria del lado local.

Debe persistirse de forma estable.

### Campos persistidos objetivo

`youtube_playlist_item` ya dispone de:

* `normalized_title`
* `normalized_artist`

`local_song` debe añadir:

* `normalized_title`
* `normalized_artist`

El adaptador hacia el contrato comparable debe mapear ambos lados a:

* `comparable_title`
* `comparable_artist`

Con esta decision:

* `normalized_*` sigue siendo un nombre de persistencia valido
* `comparable_*` pasa a ser el nombre semantico del contrato de matching

### Regla funcional

Queda eliminada la dependencia funcional de comparar:

* YouTube normalizado

contra:

* local sin normalizar

El flujo correcto pasa a comparar siempre:

* comparable YouTube normalizado
* comparable local normalizado

## Estados funcionales

### `FOUND`

Se usa cuando:

* titulo y artista ya han quedado validados
* la candidata local es defendible
* no hay ambigüedad irresoluble

Regla dura:

* no puede existir `FOUND` con artista no validado
* en titulos genericos como `intro`, `outro`, `skit`, `interludio` y similares no basta el titulo; la duracion debe ayudar a confirmar

### `POSSIBLE_MATCH`

Se usa solo cuando:

* titulo y artista ya validaron una o mas candidatas
* el score final no puede romper la ambigüedad de forma segura
* o la mejor candidata validada no alcanza confirmacion automatica pero sigue siendo la opcion mas plausible entre varias equivalentes

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

En el matcher vigente el score ya no valora ruido textual de pools amplios.

Solo puntua:

* duracion
* consistencia de una candidata ya validada
* desempate entre varias candidatas con el mismo titulo y artista

El matcher ya no decide el acceso al subconjunto.

Su responsabilidad queda reducida a:

* puntuar candidatas que ya han pasado `titulo -> artista -> reserva`
* resolver si una unica candidata queda en `FOUND`
* marcar `POSSIBLE_MATCH` cuando varias candidatas validas siguen siendo ambiguas

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
* `Titulo generico con artista valido, pero la duracion no permite confirmar FOUND.`
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
