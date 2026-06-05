# Playlist Item Matcher Service

## Contexto

La comparacion entre `youtube_playlist_item` y `local_song` necesitaba una primera heuristica clara antes de implementar el caso de uso completo.

Sin un matcher dedicado, la clasificacion `found`, `missing` y `possible_match` quedaria dispersa entre UI y aplicacion.

## Decision

Se crea `playlistItemMatcherService` como servicio puro de dominio en `app/domain/playlists/services/`.

Responsabilidad:

* comparar un item de YouTube contra una coleccion de `LocalSong`
* elegir la mejor candidata
* devolver su clasificacion, score y razon

Scoring v1:

* titulo exacto normalizado: peso alto
* artista exacto normalizado: peso alto
* coincidencia parcial por inclusion o solape de tokens: peso medio
* duracion dentro de `+- 3s`: refuerzo alto
* duracion dentro de `+- 5s`: refuerzo medio
* duracion dentro de `+- 8s`: refuerzo bajo para posibles coincidencias

Clasificacion v1:

* `found`
  * titulo fuerte
  * artista fuerte
  * y, si ambas duraciones existen, dentro de tolerancia
* `possible_match`
  * score minimo suficiente sin llegar a coincidencia fuerte
* `missing`
  * ninguna candidata supera el minimo esperado

Desempate:

* mayor score total
* mayor fuerza de titulo
* mayor fuerza de artista
* menor diferencia de duracion
* mayor `id` como criterio estable final

## Consecuencias

* el caso de uso de comparacion podra reutilizar una heuristica aislada y testeada
* la normalizacion comun se aplica a `local_song` al vuelo
* la primera version prioriza evitar falsos positivos claros antes que maximizar recall
