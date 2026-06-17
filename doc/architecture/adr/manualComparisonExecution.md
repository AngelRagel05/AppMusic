# Manual Comparison Execution

## Contexto

La comparacion de biblioteca contra playlist puede tardar bastante cuando hay miles de canciones o resultados.

Ejecutarla automaticamente al entrar en la pantalla hacia que la navegacion pareciera rota y metia trabajo costoso sin una accion explicita del usuario.

## Decision

La comparacion pasa a ser manual.

Al entrar en la pantalla:

* si hay cache previa, se muestra
* si la cache esta obsoleta, se sigue mostrando con aviso
* si no hay cache, se muestra un estado informativo

La recomparacion solo se ejecuta cuando el usuario pulsa una accion explicita de recomparacion.

El refresh barato de vista queda separado en `Refrescar snapshot`.

La accion `Recomparar pendientes`:

* recalcula solo pendientes, `MISSING`, `POSSIBLE_MATCH` e items invalidados
* genera un nuevo snapshot persistido en BBDD
* actualiza el resultado visible con la ultima comparacion guardada
* valida antes de arrancar que exista una playlist activa y una biblioteca activa
* confirma explicitamente al usuario que la ejecucion se hara contra esa pareja activa

La accion `Recomparar todo`:

* fuerza una recomputacion completa desde cero
* genera un nuevo snapshot persistido en BBDD
* confirma explicitamente que sera mas costosa que recomparar pendientes

La accion `Refrescar snapshot`:

* recarga el ultimo snapshot persistido del ambito activo
* no ejecuta el worker de comparacion
* mantiene visible si el snapshot cargado esta `fresh` o `stale`

## Consecuencias

* entrar en la pantalla deja de disparar trabajo pesado
* la navegacion es mas estable y predecible
* el usuario controla cuando asumir el coste de recalculo
* el usuario puede refrescar la vista sin pagar una recomputacion total
* el usuario distingue entre recomparacion incremental y recomputacion completa
* se evita lanzar el worker cuando falta contexto activo
* el feedback de confirmacion deja claro que el alcance siempre es la playlist activa y la biblioteca activa
