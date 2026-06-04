# ADR: Importacion manual de items de playlist en segundo plano

## Estado

Aprobada

## Contexto

La importacion de items de una playlist de YouTube puede tardar y depende de `yt-dlp`.

No debe ejecutarse directamente desde la UI ni bloquear la interfaz mientras se resuelve la playlist activa y se extraen sus items.

## Decision

La accion visible de la feature `youtubePlaylists` sera `Importar items`.

La UI delega la accion en `YoutubePlaylistsController`, que a su vez usa `YoutubePlaylistImportViewModel`.

El viewmodel arranca un `ImportYoutubePlaylistItemsWorker` dedicado para ejecutar `ImportYoutubePlaylistItemsUseCase` en segundo plano y devolver el resultado al hilo principal.

Ademas, al cargar la feature, si existe una playlist activa, el controller lanza automaticamente una importacion inicial en segundo plano para refrescar el snapshot al iniciar la aplicacion.

## Consecuencias

- La interfaz sigue respondiendo durante la importacion.
- La logica de importacion sigue fuera de `presentation`.
- El usuario recibe mensajes claros de inicio, completado y error.
- La accion de guardar/editar playlists sigue separada del flujo de importacion del snapshot.
