# ADR: Puerto de importacion de items de playlist de YouTube

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La aplicacion necesita importar items de una playlist de YouTube, pero todavia no debe acoplar la capa `application` a `yt-dlp` ni a errores tecnicos de infraestructura.

Antes de implementar el adaptador real hace falta fijar:

* el DTO que devuelve la importacion
* el contrato del importador
* la estrategia minima de errores

## Decision

Se introduce en `application`:

* `ImportedYoutubePlaylistItemDto`
* `YoutubePlaylistItemsImporterPort`
* una jerarquia minima de errores:
  * `YoutubePlaylistNotAccessibleError`
  * `YoutubePlaylistImportInvalidUrlError`
  * `YoutubePlaylistImportExtractorError`

El puerto recibe:

* `playlist_url`
* `external_playlist_id`

Y devuelve:

* lista de `ImportedYoutubePlaylistItemDto`

## Consecuencias

Ventajas:

* el caso de uso futuro no depende de `yt-dlp`
* el adaptador real puede cambiar sin romper la capa de aplicacion
* los errores funcionales quedan diferenciados desde el contrato

Costes:

* la capa `application` gana un contrato mas antes de tener implementacion real
* habra que mapear cuidadosamente los errores del extractor externo a esta jerarquia

## Fuera de alcance

En esta fase no se implementa:

* adaptador real de importacion
* caso de uso de importacion
* persistencia de items importados
