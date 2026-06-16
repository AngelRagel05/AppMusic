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
* sincronizar el snapshot previo con `replace_for_playlist(...)`

El resultado del caso de uso se resume en:

* `youtube_playlist_id`
* `playlist_title`
* `imported_item_count`
* `created_item_count`
* `updated_item_count`
* `existing_item_count`
* `removed_item_count`

La importacion compara el snapshot persistido anterior con el snapshot nuevo por `external_video_id`.

Se considera `actualizado` cualquier item ya existente cuyo `position`, titulos o metadata comparable haya cambiado entre ambas importaciones.

El contrato de persistencia del snapshot queda asi:

* si un item no cambia, conserva `id`, `created_at` y `updated_at`
* si un item cambia, conserva `id` y actualiza su contenido
* si un item desaparece del import, sale del snapshot activo

## Consecuencias

Ventajas:

* la UI futura solo tendra que disparar un caso de uso claro
* la estrategia de sincronizacion incremental queda centralizada en aplicacion
* la normalizacion se aplica antes de persistir, no despues

Costes:

* la sincronizacion necesita comparar el snapshot previo con el import nuevo
* la importacion y la comparacion siguen separadas en casos de uso distintos

## Fuera de alcance

En esta fase no se implementa:

* comparacion contra `local_song`
* worker o UI de importacion
