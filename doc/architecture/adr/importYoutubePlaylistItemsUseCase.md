# ADR: Caso de uso de importacion de items de playlist de YouTube

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La aplicacion ya dispone de:

* estructura persistible para `youtube_playlist_item`
* normalizacion minima reutilizable
* puerto de importacion y adaptador `yt-dlp`

Faltaba coordinar todo eso desde `application` sin mezclar infraestructura, normalizacion y persistencia en la UI.

## Decision

Se introduce `ImportYoutubePlaylistItemsUseCase`.

El flujo queda fijado asi:

* obtener la playlist principal activa
* validar que exista
* importar items desde `YoutubePlaylistItemsImporterPort`
* normalizar cada item importado
* construir entidades `YoutubePlaylistItem`
* reemplazar por completo el snapshot previo con `replace_for_playlist(...)`

El resultado del caso de uso se resume en:

* `youtube_playlist_id`
* `playlist_title`
* `imported_item_count`

## Consecuencias

Ventajas:

* la UI futura solo tendra que disparar un caso de uso claro
* la estrategia de snapshot completo queda centralizada en aplicacion
* la normalizacion se aplica antes de persistir, no despues

Costes:

* el flujo no conserva diferencias incrementales entre importaciones
* la importacion y la comparacion siguen separadas en casos de uso distintos

## Fuera de alcance

En esta fase no se implementa:

* comparacion contra `local_song`
* worker o UI de importacion
* estrategia incremental de sincronizacion de items
