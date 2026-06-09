# ADR: normalizacion y umbrales para matching de comparacion

## Estado

Aceptada

## Contexto

La comparacion entre playlist y biblioteca local estaba clasificando demasiados casos claros como `possible_match`.

Los patrones mas repetidos eran:

* titulos de YouTube con formato `NN. Artista - Cancion`
* sufijos `ft`, `feat` o `featuring` en el titulo de YouTube
* metadata local con artista menos fiable que el titulo

Eso hacia que coincidencias evidentes quedaran en scores de `55.0` o `75.0` y no subieran a `found`.

## Decision

Se refuerza la logica de matching en dos frentes:

* la normalizacion de comparacion elimina numeracion inicial de pista y sufijos `feat` en titulos
* la normalizacion de items de YouTube separa `artista - titulo` antes de perder el separador durante la limpieza
* la clasificacion rebaja el umbral de `found` cuando titulo, artista y duracion ya aportan una señal suficientemente fuerte
* cada comparacion recalcula la normalizacion de YouTube a partir de `raw_title` y `raw_channel_name`, sin depender exclusivamente del snapshot normalizado guardado en base de datos

## Consecuencias

Positivas:

* menos falsos `possible_match`
* mejor comportamiento con playlists importadas desde YouTube y metadata local heterogenea
* mayor prioridad al titulo real de la pista y a la duracion cuando ambos apuntan a la misma cancion

Riesgos:

* la clasificacion `found` se vuelve mas permisiva
* algunos casos con titulo repetido y artista pobremente etiquetado pueden requerir vigilancia en futuros tests

## Implementacion

Los cambios viven en:

* `app/domain/metadata/services/musicComparisonNormalizationService.py`
* `app/domain/playlists/services/youtubePlaylistItemNormalizationService.py`
* `app/domain/playlists/services/playlistItemMatchingRules.py`
