# Flujo de playlist principal de YouTube

## Objetivo

Permitir que el usuario defina una playlist principal de YouTube para usarla como referencia
al comparar su musica local.

## Flujo implementado

1. El usuario pega una URL de playlist de YouTube en la seccion `Playlists de YouTube`.
2. La aplicacion valida que la URL pertenezca a YouTube y que incluya el parametro `list`.
3. La app canoniza la URL al formato `https://www.youtube.com/playlist?list=<id>`.
4. La playlist se guarda en `youtube_playlist` y se marca como activa.
5. Si ya existia esa playlist, se reactiva y se actualiza su URL canonica.
6. El usuario puede activar despues cualquier playlist guardada desde la tabla.

## Decisiones tecnicas

* La validacion de URL vive en `DefineMainYoutubePlaylistUseCase` porque es una regla operativa
  del caso de uso y no requiere todavia una integracion externa.
* El titulo visible se genera de forma local como `Playlist <external_playlist_id>` hasta que
  exista una integracion real con YouTube o `yt-dlp` para hidratar metadata remota.
* Solo una playlist puede quedar activa al mismo tiempo, igual que ocurre con `local_folder`.

## Capas implicadas

* `presentation`: nueva seccion `youtubePlaylistsSection` y coordinacion desde `MainWindowController`
* `application`: DTOs y use cases para listar, activar, consultar activa y definir principal
* `domain`: entidad `YoutubePlaylist` y contrato `YoutubePlaylistRepository`
* `infrastructure`: repositorio SQLAlchemy para persistencia en `youtube_playlist`
