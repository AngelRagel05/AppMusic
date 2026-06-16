# Persisted Playlist Item Matcher Service

## Contexto

La comparacion entre `youtube_playlist_item` y `local_song` estaba reutilizando un matcher que normalizaba y reinterpretaba datos en caliente.

Eso mezclaba responsabilidades de:

* importacion de YouTube
* escaneo de biblioteca local
* comparacion

Ademas, el servicio recibia entidades completas cuando la comparacion solo necesitaba un subconjunto estable de datos comparables.

## Decision

Se sustituye el matcher anterior por `persistedPlaylistItemMatcherService`.

Su responsabilidad queda limitada a:

* comparar items ya persistidos en formato comparable
* elegir la mejor candidata
* devolver clasificacion, score y razon

No normaliza ni parsea metadata cruda.

## Modelo de entrada

El servicio recibe modelos comparables especificos:

* `ComparableYoutubePlaylistItem`
  * `id`
  * `normalized_title`
  * `normalized_artist`
  * `duration_seconds`
* `ComparableLocalSong`
  * `id`
  * `title`
  * `artist`
  * `duration_seconds`
  * flags operativos si hacen falta

## Consecuencias

* la comparacion deja de depender de normalizacion en tiempo de matching
* scan e import pasan a ser los unicos productores de datos comparables
* el servicio queda mas facil de probar y extender sin tocar infraestructura
* el matcher legacy y sus tests dejan de formar parte del flujo activo
