# Persisted Comparison Contract And Refresh Redesign

## Contexto

La comparacion actual entre `youtube_playlist_item` y `local_song` mezcla responsabilidades de tres flujos distintos:

* escaneo de biblioteca local
* importacion de playlist de YouTube
* comparacion

En el estado actual, la comparacion vuelve a normalizar y reinterpretar datos ya persistidos. Eso rompe la separacion de responsabilidades y dispara el coste del refresh.

Ademas, la accion de `refresh` en presentacion se comporta como una recomparacion completa, cuando funcionalmente el usuario tambien necesita una accion barata para solo recargar el snapshot persistido.

## Decision

Se fija el siguiente contrato funcional para el rediseño de comparacion persistida.

### Contrato de datos

Los campos comparables del flujo local son:

* `local_song.title`
* `local_song.artist`
* `local_song.duration_seconds`

Se consideran ya normalizados y listos para comparacion.

Los campos comparables del flujo YouTube son:

* `youtube_playlist_item.normalized_title`
* `youtube_playlist_item.normalized_artist`
* `youtube_playlist_item.duration_seconds`

Se consideran la fuente persistida y comparable del lado YouTube.

### Contrato de comparacion

La comparacion:

* no normaliza
* no parsea `raw_title`
* no reinterpreta `raw_channel_name`
* solo compara valores persistidos ya preparados

La preparacion de datos queda fuera de comparacion:

* `ScanLocalFolderUseCase` prepara y persiste el lado local
* `ImportYoutubePlaylistItemsUseCase` prepara y persiste el lado YouTube

### Contrato de refresh

Se separan dos intenciones funcionales:

* `refresh_view`
  * carga snapshot persistido e historial
  * no recalcula comparacion
* `recompare`
  * recalcula comparacion
  * puede generar un snapshot nuevo

No deben compartir el mismo significado.

### Reglas de invalidez de resultados `FOUND`

Un resultado persistido en `FOUND` se conserva mientras siga valido.

Debe invalidarse si cambia cualquiera de estas dependencias:

* version del estado importado de YouTube
* version del estado local escaneado
* version de ignored terms
* version de reglas de matching
* disponibilidad de la `local_song` enlazada
* recomparacion completa forzada por usuario o sistema

## Incrementalidad prevista

El refresh ordinario debe preferir snapshot persistido.

La recomparacion incremental prevista trabajara sobre:

* filas nuevas
* filas `missing`
* filas `possible_match`
* filas `found` invalidadas

Las filas `found` validas y sus `local_song` enlazadas quedan fuera del trabajo ordinario de recomparacion.

## Consecuencias

* la comparacion pasa a ser una responsabilidad pura de decision
* scan e import quedan como productores de datos comparables persistidos
* se habilita una ruta barata de refresh de vista
* se prepara una base coherente para incrementalidad y optimizacion posterior

## Alcance de esta fase

En esta fase se fija el contrato y su especificacion mediante:

* ADR
* politicas de refresh e invalidez
* tests de especificacion

La sustitucion completa del flujo productivo actual se ejecutara en fases posteriores.
