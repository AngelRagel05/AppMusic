# Playlist Comparison Result Persistence

## Contexto

La comparacion entre la playlist activa de YouTube y la biblioteca local ya devuelve:

* resumen
* detalle por item
* estados `found`, `missing` y `possible_match`

En este punto surge la decision de si guardar o no ese resultado en base de datos.

## Decision

Por ahora **no se persiste** el resultado de comparacion.

La comparacion se mantiene como un calculo bajo demanda:

* se ejecuta al abrir la pantalla `Comparacion`
* usa el estado actual de `youtube_playlist_item`
* usa el estado actual de `local_song`
* no crea tablas nuevas ni snapshots adicionales

## Motivos

Persistir ahora anadiria complejidad sin aportar valor claro inmediato:

* habria que invalidar resultados cuando cambie la playlist importada
* habria que invalidar resultados cuando cambie la biblioteca local
* aumentaria el riesgo de mostrar comparaciones obsoletas
* la UI actual ya puede recalcular en segundo plano sin bloquear la interfaz

## Cuando si tendria sentido persistir

Solo se reabrira esta decision si aparece un caso claro de negocio como:

* historico de comparaciones
* auditoria
* revision manual mantenida entre sesiones

## Consecuencias

* no hay migraciones nuevas para resultados de comparacion
* el resultado visible siempre representa el estado actual de playlist y biblioteca
* la complejidad de sincronizacion se mantiene baja en esta version
