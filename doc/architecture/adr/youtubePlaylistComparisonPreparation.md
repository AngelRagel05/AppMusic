# ADR: Preparacion del snapshot de playlist para comparacion futura

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La importacion de items de playlist ya persiste un snapshot local, pero la siguiente fase necesitara consumir ese snapshot desde aplicacion para compararlo contra `local_song`.

Antes de implementar el matching conviene cerrar dos decisiones:

* el snapshot debe exponer ya los campos comparables
* debe existir un caso de uso explicito para leer los items de la playlist activa

## Decision

Se mantiene `youtube_playlist_item` como snapshot listo para comparacion con estos campos minimos:

* `normalized_title`
* `normalized_artist`
* `duration_seconds`

Ademas se añade `ListActiveYoutubePlaylistItemsUseCase` como punto de lectura desde aplicacion para recuperar el snapshot de la playlist activa sin acoplar casos futuros a la capa de persistencia.

Tambien se deja definido `CompareYoutubePlaylistWithLocalLibraryUseCase` como siguiente caso de uso de la cadena, aunque su matching todavia no se implementa en esta fase.

## Consecuencias

Ventajas:

* la comparacion posterior puede arrancar desde un caso de uso ya estable
* el snapshot ya entrega los datos comparables sin recalculo adicional
* se evita que la logica futura dependa directamente del repositorio SQLAlchemy

Limitaciones:

* todavia no existe score de matching ni resultado de comparacion persistido
* el caso de uso de comparacion queda solo definido, no ejecutable todavia
