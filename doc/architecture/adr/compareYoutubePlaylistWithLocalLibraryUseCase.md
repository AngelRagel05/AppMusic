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
* crea una cabecera `playlist_comparison`
* persiste una fila `playlist_comparison_result` por cada item evaluado
* devuelve `PlaylistComparisonResultDto`

El resultado contiene:

* `summary`
* `items`

## Consecuencias

* la comparacion se calcula bajo demanda
* el flujo queda desacoplado de la UI
* el resultado queda persistido como snapshot reutilizable
* la disponibilidad de una cancion local influye directamente en el matching
* cada item conserva su `score` para uso posterior
