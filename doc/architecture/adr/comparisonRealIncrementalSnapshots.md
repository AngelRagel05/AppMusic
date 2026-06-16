# Comparison Real Incremental Snapshots

## Contexto

La congelacion de `FOUND` redujo parte del coste, pero todavia habia un problema estructural:

* el snapshot de `youtube_playlist_item` se destruia y recreaba entero en cada import
* eso regeneraba ids y timestamps incluso para items sin cambios
* por tanto, la comparacion no podia distinguir con fiabilidad entre item nuevo, item cambiado e item intacto

Sin identidad estable en el snapshot importado, la incrementalidad real entre imports era falsa.

## Decision

Se fija este contrato incremental:

### Snapshot de YouTube persistido

`YoutubePlaylistItemRepository.replace_for_playlist(...)` deja de ser un borrado total y pasa a comportarse como una sincronizacion por `external_video_id`.

Reglas:

* si el item ya existe y no cambia, conserva `id`, `created_at` y `updated_at`
* si el item ya existe y cambia, conserva `id` y actualiza su contenido
* si el item es nuevo, se crea
* si el item desaparece del import, se elimina del snapshot activo

### Snapshot compuesto de comparacion

`CompareYoutubePlaylistWithLocalLibraryUseCase` construye cada nuevo snapshot como una composicion de:

* filas `FOUND` previas todavia validas, copiadas sin matcher
* filas que requieren recomputacion, recalculadas contra el estado persistido actual

Las filas recalculadas son:

* items nuevos
* items que venian en `MISSING`
* items que venian en `POSSIBLE_MATCH`
* items `FOUND` invalidados
* cualquier fila cuando se pide `force_full_recompute=True`

### Politica de estabilidad de asignaciones

Un `FOUND` valido no se rompe solo porque aparezca una cancion local potencialmente mejor.

Solo se reabre si:

* cambia el item de YouTube
* cambia la cancion local enlazada
* la cancion local deja de estar disponible
* cambian `ignored_terms`
* cambian las reglas de matching
* se fuerza recomputacion completa

## Consecuencias

* la comparacion incremental ya puede sobrevivir a imports repetidos sin invalidar todo
* el snapshot nuevo conserva solo las filas que siguen siendo validas y sustituye las recalculadas
* la politica de ruptura de asignaciones queda explicita y testeable
