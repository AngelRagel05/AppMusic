# ADR: Snapshot persistido de items de playlist de YouTube

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La aplicacion ya permite guardar una playlist de YouTube como referencia, pero todavia no persistia sus items individuales.

Para poder comparar la playlist contra `local_song`, hace falta almacenar un snapshot local de los items importados con los datos utiles para matching posterior.

Ademas, YouTube suele mezclar informacion musical y textual en el titulo o en el canal, por lo que conviene conservar tanto el dato bruto como una forma normalizada.

## Decision

Se redefine `youtube_playlist_item` como tabla de snapshot por playlist.

La estructura nueva guarda:

* `external_video_id`
* `position`
* `raw_title`
* `raw_channel_name`
* `normalized_title`
* `normalized_artist`
* `duration_seconds`
* `published_at`

Se fijan dos decisiones tecnicas:

* cada importacion futura reemplazara el snapshot completo de items de la playlist
* `normalized_title` y `normalized_artist` se persisten desde la importacion, no se calculan solo al comparar

## Consecuencias

Ventajas:

* la comparacion futura contra `local_song` parte de datos ya preparados
* se conserva el dato bruto original para depuracion o mejoras de normalizacion
* el modelo deja de depender de campos poco fiables para este caso como `release_year`

Costes:

* hay que migrar la estructura previa de `youtube_playlist_item`
* aparece una duplicidad intencional entre dato bruto y dato normalizado

## Fuera de alcance

En esta fase no se implementa:

* importacion real desde YouTube
* comparacion contra `local_song`
* estrategia incremental de sincronizacion de items
