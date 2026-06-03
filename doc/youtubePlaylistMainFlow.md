# Flujo de playlist principal de YouTube

## Objetivo

Permitir que el usuario defina una playlist principal de YouTube para usarla como referencia
al comparar su musica local.

## Flujo implementado

1. El usuario introduce un nombre visible y pega una URL de playlist de YouTube en la seccion `Playlists de YouTube`.
2. La aplicacion valida que el nombre no este vacio.
3. La aplicacion valida que la URL pertenezca a YouTube y que incluya el parametro `list`.
4. La app canoniza la URL al formato `https://www.youtube.com/playlist?list=<id>`.
5. La playlist se guarda en `youtube_playlist`, usando `title` como nombre visible y `external_playlist_id` como id externo de YouTube, y se marca como activa.
6. Si ya existia esa playlist, se reactiva y se actualizan su nombre y su URL canonica.
7. El usuario puede activar despues cualquier playlist guardada desde la tabla.

## Decisiones tecnicas

* La validacion de URL vive en `DefineMainYoutubePlaylistUseCase` porque es una regla operativa
  del caso de uso y no requiere todavia una integracion externa.
* `title` guarda el nombre visible definido por el usuario.
* `external_playlist_id` guarda solo el id que viene de YouTube.
* Solo una playlist puede quedar activa al mismo tiempo, igual que ocurre con `local_folder`.

## Capas implicadas

* `presentation`: nueva seccion `youtubePlaylistsSection` y coordinacion desde `MainWindowController`
* `application`: DTOs y use cases para listar, activar, consultar activa y definir principal
* `domain`: entidad `YoutubePlaylist` y contrato `YoutubePlaylistRepository`
* `infrastructure`: repositorio SQLAlchemy para persistencia en `youtube_playlist`
