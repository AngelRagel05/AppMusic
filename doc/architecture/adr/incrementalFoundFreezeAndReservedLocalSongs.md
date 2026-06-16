# Incremental Found Freeze And Reserved Local Songs

## Contexto

La recomparacion completa seguia recorriendo items ya resueltos en `FOUND` y seguia ofreciendo como candidatas canciones locales que ya estaban asignadas.

Con bibliotecas grandes, eso agranda innecesariamente el universo de comparacion y mete trabajo repetido en cada nueva ejecucion.

## Decision

La comparacion persistida pasa a reutilizar el ultimo snapshot del scope activo para construir una recomparacion incremental.

Reglas:

* si una fila previa esta en `FOUND` y sigue valida, no se recompara
* su `local_song_id` queda reservado y sale del pool de candidatas
* solo se recomparan:
  * items sin resolver previo
  * items `FOUND` invalidados
  * items que no tengan una `local_song` reservada valida
* la aparicion de una cancion local potencialmente mejor no reabre por si sola un `FOUND` valido
* para romper una asignacion valida hace falta invalidacion explicita o recomputacion completa forzada

## Metadatos persistidos de snapshot

La cabecera `playlist_comparison` persiste:

* `youtube_playlist_imported_at`
* `local_library_scanned_at`
* `ignored_terms_version`
* `matching_rules_version`

Estos metadatos permiten decidir si una fila `FOUND` previa sigue siendo reutilizable.

## Reglas de invalidacion

Una fila previa `FOUND` se reabre si ocurre cualquiera de estas condiciones:

* la `local_song` enlazada deja de estar disponible
* la `local_song` enlazada cambia despues de `local_library_scanned_at`
* el `youtube_playlist_item` cambia despues de `youtube_playlist_imported_at`
* cambia `ignored_terms_version`
* cambia `matching_rules_version`

Si no cambia ninguna dependencia, la fila queda congelada y se copia al snapshot nuevo sin pasar por el matcher.

## Consecuencias

* baja el numero real de comparaciones por ejecucion
* se evita reutilizar la misma `local_song` en mas de un `FOUND`
* el comportamiento manual en `FOUND` deja de perderse mientras siga valido
* los snapshots legacy sin metadatos quedan en modo conservador y no congelan `FOUND`
