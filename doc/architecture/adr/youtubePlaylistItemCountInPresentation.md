# ADR: Conteo de items por playlist en presentacion

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La pantalla de playlists de YouTube necesita mostrar cuántos items tiene cada playlist guardada.

Ese dato ya existe implícitamente en `youtube_playlist_item`, pero no estaba expuesto en los DTOs de playlist ni en los casos de uso de lectura.

## Decision

Se añade `item_count` a `YoutubePlaylistDto`.

Los casos de uso `ListYoutubePlaylistsUseCase` y `GetActiveYoutubePlaylistUseCase` consultan el repositorio de `youtube_playlist_item` para enriquecer cada playlist con su número de items importados.

## Consecuencias

Ventajas:

* la UI no accede directamente a persistencia
* el conteo queda disponible tanto en la lista de playlists como en la tarjeta de playlist activa
* la solución reutiliza la capa de aplicación ya existente

Costes:

* los casos de uso de lectura de playlists dependen también del repositorio de items
