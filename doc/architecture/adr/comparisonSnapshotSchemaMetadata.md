# Comparison Snapshot Schema Metadata

## Contexto

La comparacion incremental ya distinguia dependencias logicas con:

* `matching_rules_version`
* `ignored_terms_version`
* timestamps del snapshot local y del snapshot YouTube

Eso era suficiente para invalidar muchos casos, pero dejaba ambigüedad de auditoria y de identidad del estado comparado:

* dos snapshots podian compartir semantica de reglas pero no exponer una huella explicita del estado local
* lo mismo para el estado persistido de `youtube_playlist_item`

Ademas, aparecio la duda de si habia que persistir flags por fila como `is_locked_found` o `invalidated_reason`.

## Decision

### Metadatos nuevos en `playlist_comparison`

La cabecera del snapshot persiste tambien:

* `youtube_playlist_state_fingerprint`
* `local_library_state_fingerprint`

Ambos fingerprints describen el estado persistido realmente comparado en esa ejecucion.

Objetivos:

* trazabilidad
* identidad estable del snapshot
* soporte para comparaciones futuras y diagnostico

### Sin flags nuevas por fila en `playlist_comparison_result`

No se añaden columnas como:

* `is_locked_found`
* `invalidated_reason`

Estas piezas deben seguir siendo estado derivado de:

* `match_status`
* `matched_by`
* dependencias de cabecera del snapshot
* estado actual de `local_song`
* estado actual de `youtube_playlist_item`

Persistirlas duplicaria logica, obligaria a resincronizacion y haria el modelo mas fragil.

### Indices

Se fija un indice compuesto adicional:

* `playlist_comparison (youtube_playlist_id, local_folder_id, compared_at, id)`

Ese es el patron principal de lectura para:

* `find_latest_for_scope`
* `list_for_scope`
* politica de retencion

## Consecuencias

* la cabecera del snapshot pasa a describir mejor el estado comparado
* el detalle por fila mantiene un modelo compacto y sin columnas redundantes
* la busqueda del ultimo snapshot por scope queda alineada con el uso real
