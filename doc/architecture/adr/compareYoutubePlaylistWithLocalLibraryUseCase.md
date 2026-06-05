# Compare Youtube Playlist With Local Library Use Case

## Contexto

La aplicacion ya tenia:

* snapshot importado de `youtube_playlist_item`
* canciones locales en `local_song`
* normalizacion comun
* matcher de dominio

Faltaba coordinar ambas fuentes en un caso de uso de aplicacion que devolviera resumen y detalle listos para presentation.

## Decision

`CompareYoutubePlaylistWithLocalLibraryUseCase`:

* obtiene la playlist activa
* obtiene la biblioteca local activa
* lee items importados de la playlist
* lee canciones locales de la carpeta activa
* filtra solo `local_song.is_available = true`
* ejecuta el matcher en memoria por cada item de YouTube
* devuelve `PlaylistComparisonResultDto`

El resultado contiene:

* `summary`
* `items`

No se persiste todavia el resultado de comparacion.

## Consecuencias

* la comparacion se calcula bajo demanda
* el flujo queda desacoplado de la UI
* la primera version evita introducir tablas nuevas para resultados
* la disponibilidad de una cancion local influye directamente en el matching
