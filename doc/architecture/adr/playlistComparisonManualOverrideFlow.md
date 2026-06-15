# Playlist Comparison Manual Override Flow

## Contexto

La comparacion persistida ya guarda en `playlist_comparison_result`:

* `match_status`
* `local_song_id`
* `score`
* `matched_by`

El siguiente paso funcional permite que el usuario corrija manualmente una fila concreta sin recalcular toda la comparacion.

## Decision

La edicion manual se resuelve con un caso de uso especifico:

* `UpdatePlaylistComparisonResultUseCase`

La UI no escribe SQL ni muta modelos ORM directamente.

El caso de uso:

* carga la cabecera `playlist_comparison` por `playlist_comparison_id`
* carga la fila objetivo por `playlist_comparison_id + youtube_playlist_item_id`
* valida coherencia entre `match_status` y `local_song_id`
* valida que la `local_song` elegida pertenezca al `local_folder_id` del snapshot
* actualiza solo esa fila a traves de `PlaylistComparisonResultRepository.update_match_decision(...)`
* conserva el `score` automatico previo
* cambia `matched_by` a un codigo controlado con prefijo `manual:`

La implementacion de persistencia:

* localiza la fila por `playlist_comparison_id + youtube_playlist_item_id`
* modifica `match_status`, `local_song_id` y `matched_by`
* deja `score` intacto
* persiste el cambio puntual y devuelve la entidad actualizada

Listado de canciones locales seleccionables:

* no se crea un caso de uso nuevo mientras ya exista `ListActiveLocalSongsUseCase`
* la pantalla reutiliza la coleccion de canciones activas que ya queda cargada en cache junto al snapshot de comparacion
* el modal filtra localmente por `title`, `artist`, `album`, `file_name` y `file_path`
* la seleccion siempre nace desde el resultado de playlist hacia una `local_song`, nunca al reves

Filtros de visibilidad manual:

* la tabla mantiene `all`, `matched`, `missing` y `possible_match`
* se añaden `manual` y `automatic`
* el criterio sale de `matched_by`
* `matched_by` con prefijo `manual:` entra en `manual`
* `matched_by` con prefijo `auto:` entra en `automatic`
* los snapshots legacy sin prefijo manual se consideran `automatic` para no exigir migracion ni columna nueva

## No migracion

No hace falta migracion adicional para esta fase.

La tabla actual ya soporta el flujo porque dispone de:

* `playlist_comparison_id`
* `youtube_playlist_item_id`
* `local_song_id`
* `match_status`
* `score`
* `matched_by`

## Reglas operativas

* `missing` obliga `local_song_id = NULL`
* `found` obliga `local_song_id` informado
* `possible_match` admite `local_song_id` nulo o informado
* si la cancion local elegida no pertenece al folder del snapshot, la actualizacion se rechaza
* cuando la fila queda en estado manual, `score` se conserva como referencia historica y deja de ser el arbitro del estado final

## Consecuencias

* la logica de correccion manual queda aislada en aplicacion
* la intencion de persistencia manual queda expresada en un metodo de repositorio especifico, no en un `update` generico
* el flujo es reutilizable desde controller, viewmodel o futuros dialogs sin duplicar validaciones
* el snapshot persistido mantiene trazabilidad de que parte fue automatica y que parte fue corregida manualmente

## Rehidratacion persistida

Al reabrir la app, `LoadPersistedPlaylistComparisonUseCase` debe respetar exactamente la fila persistida:

* `match_status` manual sigue siendo el estado final mostrado en UI
* `local_song_id` manual sigue siendo la cancion enlazada del resultado
* `matched_by` manual se traduce a un motivo legible de UI, sin perder el codigo persistido
* si la cancion enlazada existe en BBDD pero no forma parte de la lista seleccionable visible, el snapshot igualmente la rehidrata para mostrar el enlace en detalle

Esto garantiza consistencia en:

* reinicio de app
* carga del ultimo snapshot
* filtros `manual` y `automatic`
* modal de detalle del resultado

## Coexistencia entre calculo automatico y correccion manual

La correccion manual vive solo dentro del snapshot persistido que el usuario esta editando.

Cuando el usuario relanza una comparacion completa:

* se crea un snapshot nuevo
* el matcher recalcula todas las filas desde cero
* no se reaplican overrides manuales del snapshot anterior
* el snapshot anterior conserva sus decisiones manuales mientras siga retenido por la politica de historico

Se elige esta regla porque:

* evita migrar overrides entre snapshots con items que pueden haber cambiado
* mantiene simple el caso de uso de comparacion
* evita mezclar estado automatico nuevo con decisiones manuales antiguas sin trazabilidad adicional

Si en el futuro se quiere persistencia transversal real de overrides entre refresh, eso requerira una tabla especifica de decisiones manuales desacoplada del snapshot.
