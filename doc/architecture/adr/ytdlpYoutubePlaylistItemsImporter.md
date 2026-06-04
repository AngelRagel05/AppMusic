# ADR: Adaptador `yt-dlp` para importar items de playlist de YouTube

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La aplicacion ya dispone de un puerto `YoutubePlaylistItemsImporterPort`, pero todavia faltaba una implementacion concreta en infraestructura para resolver items reales desde YouTube.

La dependencia disponible en el proyecto para este trabajo es `yt-dlp`.

## Decision

Se implementa `YtDlpYoutubePlaylistItemsImporter` en `app/infrastructure/downloads/youtube/`.

El adaptador:

* acepta `playlist_url` o `external_playlist_id`
* construye una URL canonica cuando solo recibe `external_playlist_id`
* llama a `yt-dlp` en modo `extract_flat`
* mapea los resultados a `ImportedYoutubePlaylistItemDto`
* no persiste nada
* no compara nada

El tratamiento de errores queda asi:

* validacion minima propia para URLs claramente invalidas
* traduccion de `DownloadError` a errores del puerto de aplicacion
* encapsulacion de fallos inesperados como `YoutubePlaylistImportExtractorError`

## Consecuencias

Ventajas:

* `application` sigue desacoplada de `yt-dlp`
* la importacion real ya existe sin invadir casos de uso con detalles tecnicos
* los tests unitarios pueden cubrir mapeo y errores con dobles, sin depender de red

Costes:

* la traduccion de errores de `yt-dlp` es parcialmente heuristica
* algunos campos opcionales dependen de la forma exacta en que `yt-dlp` entregue la entrada

## Fuera de alcance

En esta fase no se implementa:

* caso de uso de importacion
* persistencia del snapshot importado
* tests de red reales contra YouTube
