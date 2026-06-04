# Integraciones externas

## Integraciones actuales en dependencias

### Persistencia

* `SQLite`
* `SQLAlchemy`
* `Alembic`

Estado actual:

* la persistencia real esta agrupada en `app/infrastructure/persistence/`
* la configuracion principal sale de `DATABASE_URL`

### Descargas

* `yt-dlp`
* `ffmpeg-python`
* binario `ffmpeg`

Estado actual:

* existe la agrupacion `app/infrastructure/downloads/`
* `FFMPEG_PATH` ya es configurable en settings
* `YtDlpYoutubePlaylistItemsImporter` ya implementa la importacion real de items de playlist en `app/infrastructure/downloads/youtube/`
* la aplicacion define `YoutubePlaylistItemsImporterPort` como contrato para desacoplar el caso de uso de `yt-dlp`

### Metadata

* `Mutagen`

Estado actual:

* `app/infrastructure/metadata/` ya contiene `MutagenLocalSongMetadataReader`
* el escaneo local usa `Mutagen` para poblar `title`, `artist`, `album`, `release_year`, `track_number_album` y `duration_seconds`
* cada reescaneo relee esa metadata para mantener `local_song` sincronizada con los tags actuales del MP3

### Filesystem

Estado actual:

* existe `app/infrastructure/filesystem/`
* `LocalMusicScanner` recorre recursivamente la carpeta activa y detecta archivos `.mp3`

### Audio

* el objetivo arquitectonico contempla `pygame`

Estado actual:

* existe `app/infrastructure/audio/` como espacio reservado
* no hay integracion activa implementada todavia

### Red y utilidades tecnicas

* `httpx`
* `python-dotenv`
* `loguru`

Uso actual:

* `python-dotenv` carga configuracion desde entorno
* `loguru` se usa a traves de `app/shared/utils/logging.py`
* `httpx` queda disponible para futuras integraciones externas

## Reglas de encapsulacion

* ninguna ventana o widget debe hablar directamente con estas librerias
* los adaptadores concretos deben vivir en `app/infrastructure/`
* `application/` solo debe depender de contratos o protocolos cuando haga falta
* `domain/` no debe conocer estas librerias

## Contrato de importacion de playlists de YouTube

Para la futura importacion de items de playlist:

* `application` depende de `YoutubePlaylistItemsImporterPort`
* el puerto devuelve `ImportedYoutubePlaylistItemDto`
* el puerto expone errores diferenciados para:
  * playlist no accesible
  * URL invalida
  * fallo del extractor externo

Eso permite que el caso de uso traduzca feedback funcional sin depender de `yt-dlp`, red o formato de excepcion del adaptador concreto.


## Documentos relacionados

* `doc/architecture/adr/infrastructureAdapterReorganization.md`
* `doc/architecture/adr/layerDependencyRules.md`
* `doc/architecture/adr/scanLocalFolderV1Scope.md`
* `doc/architecture/adr/localSongMetadataExtraction.md`
