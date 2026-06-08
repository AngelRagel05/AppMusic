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
* guarda `score`
* deja `matched_by` como campo reservado para enriquecer la trazabilidad mas adelante

La comparacion:

* se ejecuta desde la accion manual del usuario en la pantalla `Comparacion`
* usa el estado actual de `youtube_playlist_item`
* usa el estado actual de `local_song`
* genera un snapshot persistido de ese estado comparado

Ademas, la aplicacion puede consultar varias cabeceras `playlist_comparison` del mismo ambito activo para construir un historico reciente de ejecuciones.

## Motivos

Persistir ahora aporta valor funcional directo:

* permite conservar la puntuacion de similitud por item
* deja una base clara para futuras revisiones manuales o auditoria ligera
* desacopla el calculo del consumo posterior del resultado
* reutiliza tablas ya presentes en el esquema relacional del proyecto
* permite exponer al usuario un historico resumido de comparaciones por playlist y biblioteca activas

## Gestion de obsolescencia

La persistencia no elimina la necesidad de invalidar visualmente resultados cuando cambian playlist o biblioteca.

La aplicacion debe tratar el snapshot como el resultado de una ejecucion concreta, no como verdad siempre actualizada.

## Consecuencias

* cada comparacion crea una cabecera `playlist_comparison`
* cada item comparado genera un `playlist_comparison_result`
* `score` queda disponible para analitica, depuracion y futuras reglas de UI
* la aplicacion debe seguir controlando cuando un resultado persistido esta obsoleto
* el historico visible se construye leyendo varias ejecuciones del mismo ambito activo
