# Contexto de Playlist de YouTube

## Objetivo

Unificar la documentacion sobre definicion de playlist principal, importacion de items, snapshot persistido y normalizacion de datos de YouTube.

## Flujo funcional

1. el usuario define o reactiva una playlist principal
2. la app valida y canoniza la URL
3. la playlist se persiste en `youtube_playlist`
4. se importan items externos a `youtube_playlist_item`
5. cada item conserva dato bruto y dato comparable
6. ese snapshot se usa despues por el flujo de comparacion

## Persistencia principal

### `youtube_playlist`

Guarda:

* nombre visible
* URL canonica
* `external_playlist_id`
* estado activo

Regla operativa:

* solo una playlist puede estar activa al mismo tiempo

### `youtube_playlist_item`

Guarda snapshot estable de los items importados:

* `raw_title`
* `raw_channel_name`
* `normalized_title`
* `normalized_artist`
* `duration_seconds`
* `published_at`
* `position`
* `external_video_id`

## Normalizacion

El flujo YouTube debe producir datos comparables antes del matching.

Reglas activas:

* conservar el dato bruto para depuracion
* producir `normalized_title`
* producir `normalized_artist`
* separar decoradores, ruido editorial y variantes irrelevantes
* mantener la comparacion fuera del importador

La normalizacion de YouTube no decide por si sola el matching final.

Solo prepara el snapshot para que el flujo de comparacion trabaje con datos comparables.

## Casos de uso implicados

* definir playlist principal
* activar playlist
* importar items de playlist
* listar playlist activa
* listar items activos importados

## Relacion con comparacion

La comparacion no debe reinterpretar `raw_title` ni `raw_channel_name`.

Debe consumir directamente el snapshot comparable ya preparado.

La referencia funcional de ese matching vive en:

* [comparisonContext.md](./comparisonContext.md)

