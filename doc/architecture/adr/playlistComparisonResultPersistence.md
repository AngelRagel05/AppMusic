# Playlist Comparison Result Persistence

## Contexto

La comparacion entre la playlist activa de YouTube y la biblioteca local ya devuelve:

* resumen
* detalle por item
* estados `found`, `missing` y `possible_match`
* una puntuacion numerica de similitud por cada item evaluado

En este punto la aplicacion ya necesita conservar el resultado para reutilizarlo entre sesiones y dejar trazabilidad de la ultima revision ejecutada.

## Decision

Se persiste cada ejecucion de comparacion en base de datos.

La comparacion sigue siendo un calculo bajo demanda, pero al finalizar:

* crea una cabecera en `playlist_comparison`
* crea una fila en `playlist_comparison_result` por cada `youtube_playlist_item`
* guarda `match_status`
* guarda `local_song_id` si existe cancion enlazada
* guarda `score`
* usa `matched_by` como origen controlado de la decision final

La misma fila persistida admite ajuste manual posterior sin recalcular todo el snapshot.

El flujo de correccion manual siempre nace desde un `youtube_playlist_item` ya comparado:

* el usuario parte de un resultado de playlist
* revisa el detalle
* decide el `match_status`
* y opcionalmente enlaza una `local_song`

Convencion inicial de `matched_by`:

* automatico:
  * `auto:title_artist_duration`
  * `auto:ambiguous`
  * `auto:no_competitive_candidate`
* manual:
  * `manual:user_linked_local_song`
  * `manual:user_marked_found`
  * `manual:user_marked_missing`
  * `manual:user_marked_possible`

Validaciones de aplicacion sobre la fila persistida:

* `match_status = missing` obliga `local_song_id = NULL`
* `match_status = found` obliga `local_song_id` informado
* `match_status = possible_match` permite `local_song_id = NULL`, aunque puede venir informado si el usuario eligio una candidata concreta
* si la fila se corrige manualmente, `matched_by` debe pasar a un codigo con prefijo `manual:`
* los snapshots legacy con texto humano previo en `matched_by` siguen siendo legibles al rehidratar, pero no deben volver a generarse como formato nuevo

Decision sobre `score` tras edicion manual:

* se conserva el `score` automatico si ya existia
* el `score` deja de ser autoridad funcional cuando `matched_by` usa prefijo `manual:`
* la verdad de estado final pasa a `match_status + local_song_id + matched_by`

La comparacion:

* se ejecuta desde la accion manual del usuario en la pantalla `Comparacion`
* usa el estado actual de `youtube_playlist_item`
* usa el estado actual de `local_song`
* genera un snapshot persistido de ese estado comparado

La edicion manual:

* actua solo sobre la fila del snapshot actual
* modifica `match_status`, `local_song_id` y `matched_by`
* no crea una tabla nueva en esta fase
* no se reaplica automaticamente sobre snapshots futuros

Ademas, la aplicacion puede consultar varias cabeceras `playlist_comparison` del mismo ambito activo para construir un historico reciente de ejecuciones.
La pantalla de comparacion debe exponer de forma directa la fecha y hora de la ultima comparacion ejecutada sin obligar al usuario a inspeccionar toda la lista historica.

## Motivos

Persistir ahora aporta valor funcional directo:

* permite conservar la puntuacion de similitud por item
* deja una base clara para futuras revisiones manuales o auditoria ligera
* separa el motivo humano mostrado en UI del origen tecnico persistido
* desacopla el calculo del consumo posterior del resultado
* reutiliza tablas ya presentes en el esquema relacional del proyecto
* permite exponer al usuario un historico resumido de comparaciones por playlist y biblioteca activas
* permite mostrar en cabecera cuando se ejecuto por ultima vez la comparacion vigente
* permite distinguir con claridad que parte del resultado viene del matcher y que parte fue corregida por el usuario

## Gestion de obsolescencia

La persistencia no elimina la necesidad de invalidar visualmente resultados cuando cambian playlist o biblioteca.

La aplicacion debe tratar el snapshot como el resultado de una ejecucion concreta, no como verdad siempre actualizada.

## Consecuencias

* cada comparacion crea una cabecera `playlist_comparison`
* cada item comparado genera un `playlist_comparison_result`
* `score` queda disponible para analitica, depuracion y futuras reglas de UI
* `matched_by` permite distinguir si una fila fue resuelta automaticamente o corregida manualmente
* la aplicacion debe seguir controlando cuando un resultado persistido esta obsoleto
* el historico visible se construye leyendo varias ejecuciones del mismo ambito activo
* la UI puede destacar la ultima ejecucion con una referencia temporal explicita
* los overrides manuales no sobreviven a un refresh completo mas alla del snapshot concreto en el que fueron guardados
