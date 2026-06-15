# ADR: retencion de snapshots de comparacion

## Estado

Aprobada

## Contexto

Cada ejecucion de comparacion genera:

* una cabecera en `playlist_comparison`
* una fila por item en `playlist_comparison_result`

Como cada snapshot persiste el detalle completo de la playlist comparada, el crecimiento es lineal:

* `numero de items comparados`
* multiplicado por
* `numero de comparaciones ejecutadas`

Eso hace muy facil llegar a decenas o cientos de miles de filas en
`playlist_comparison_result` sin aportar un valor proporcional al usuario.

El producto necesita:

* reutilizar el ultimo snapshot al arrancar
* mostrar un historico reciente corto
* evitar crecimiento ilimitado del almacenamiento

## Decision

Se define una politica explicita de retencion de snapshots de comparacion.

### Ambito de retencion

La retencion se calcula por scope:

* `youtube_playlist_id`
* `local_folder_id`

Es decir, cada combinacion `playlist + biblioteca` mantiene su propio historico corto.

### Maximo retenido

Se conservaran solo las ultimas `3` comparaciones por scope.

### Unidad retenida

La unidad de retencion es el snapshot completo:

* cabecera `playlist_comparison`
* todas sus filas hijas en `playlist_comparison_result`

No se retienen cabeceras sin detalle ni detalle huérfano.

### Punto de ejecucion

La retencion debe ejecutarse:

* despues de persistir una nueva comparacion completa
* dentro del flujo de `CompareYoutubePlaylistWithLocalLibraryUseCase`

El orden esperado es:

1. crear nueva cabecera `playlist_comparison`
2. guardar todas las filas `playlist_comparison_result`
3. identificar comparaciones antiguas excedentes del mismo scope
4. borrar primero resultados hijos
5. borrar despues cabeceras antiguas
6. hacer `commit` final cuando el snapshot nuevo y la purga hayan terminado

### Coherencia transaccional

La persistencia del snapshot nuevo y la purga del historico deben compartir una unica transaccion.

Eso implica:

* no hacer `commit` al guardar solo las filas hijas
* no dejar una comparacion nueva confirmada sin haber aplicado la retencion
* no borrar snapshots antiguos si falla la persistencia del snapshot nuevo

## Por que no se guarda historico ilimitado

No se adopta historico ilimitado porque:

* el usuario no necesita una trazabilidad larga para este caso de uso
* el snapshot es voluminoso por naturaleza
* la tabla `playlist_comparison_result` crece demasiado rapido
* aumenta el peso del `.db` sin mejorar la experiencia principal
* complica mantenimiento, backup y tiempos de lectura futuros

## Por que se elige 3

Se elige `3` como equilibrio entre utilidad y control de crecimiento:

* `1` seria demasiado agresivo
* `2` es valido, pero deja muy poco margen de recuperacion
* `3` permite:
  * usar el ultimo snapshot al arrancar
  * mostrar historico reciente
  * conservar una referencia inmediatamente anterior
  * limitar claramente el crecimiento

## Que se borra exactamente

Cuando un scope supera el limite:

* se conservan las `3` comparaciones mas recientes por `compared_at desc, id desc`
* se eliminan las comparaciones mas antiguas del mismo scope
* por cada comparacion eliminada se borran todas sus filas en
  `playlist_comparison_result`

No deben tocarse:

* comparaciones de otra playlist
* comparaciones de otra biblioteca
* snapshots mas recientes dentro del mismo scope

## Impacto en historico y snapshot de arranque

### Historico visible

El historico reciente pasa a estar acotado por persistencia real.

La UI seguira mostrando historico reciente, pero el maximo recuperable por scope sera `3`.

### Snapshot al arrancar

El arranque no cambia funcionalmente:

* se sigue cargando la ultima comparacion persistida del scope activo
* simplemente ya no existira un historico ilimitado detras

## Sustitucion aplicada

La implementacion se apoya en:

* soporte en repositorios para localizar snapshots excedentes por scope
* borrado seguro de hijos y cabeceras
* cierre de transaccion al final del flujo de comparacion
* tests de retencion por scope

## Implementacion relacionada

La politica queda fijada en aplicacion mediante:

* `CompareYoutubePlaylistWithLocalLibraryUseCase.SNAPSHOT_RETENTION_LIMIT = 3`
* purga por scope inmediatamente despues de persistir el nuevo snapshot completo
* `commit` final despues de guardar resultados y borrar snapshots excedentes

### Borrado coordinado

El borrado del historico no se delega a una cascada automatica de ORM ni a una limpieza externa.

La aplicacion coordina la eliminacion de forma explicita:

1. localiza comparaciones excedentes del scope activo
2. borra primero las filas hijas de `playlist_comparison_result`
3. borra despues las cabeceras de `playlist_comparison`
4. confirma todo en una unica transaccion

Esto mantiene la responsabilidad de retencion en el flujo de negocio y evita afectar scopes ajenos.
