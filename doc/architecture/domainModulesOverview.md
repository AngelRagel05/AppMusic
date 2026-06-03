# Modulos del dominio

## Modulos actuales

### `library`

Responsabilidad:

* bibliotecas locales
* carpeta principal
* activacion y mantenimiento de la biblioteca

Piezas actuales:

* `LocalFolder`
* `LocalFolderRepository`

### `playlists`

Responsabilidad:

* playlists de YouTube de referencia
* activacion, actualizacion y seleccion de playlist principal

Piezas actuales:

* `YoutubePlaylist`
* `YoutubePlaylistRepository`

### `filters`

Responsabilidad:

* terminos ignorados
* limpieza previa de ruido funcional

Piezas actuales:

* `IgnoredTerm`
* `IgnoredTermRepository`

## Modulos previstos

### `downloads`

Para estados y reglas de descarga cuando exista dominio real asociado a `yt-dlp` y `ffmpeg`.

### `metadata`

Para normalizacion y reglas de metadata cuando exista dominio real asociado a `Mutagen`.

### `playback`

Para estado y acciones de reproduccion cuando la reproduccion deje de ser solo un detalle tecnico.

## Documento detallado

La definicion detallada y el mapa completo estan en:

* [domainModuleMap.md](./domainModuleMap.md)
* [domainModularReorganization.md](./domainModularReorganization.md)
