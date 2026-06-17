# Comparison UI Actions And Snapshot Feedback

## Contexto

La pantalla de comparacion ya separaba `Refrescar snapshot` de `Recomparar`, pero todavia quedaban dos problemas:

* la UX no hacia visible la diferencia entre recomparacion incremental y recomputacion completa
* el usuario no veia con claridad por que un snapshot habia quedado obsoleto

Eso dejaba margen a expectativas rotas sobre coste, alcance y estado real del snapshot mostrado.

## Decision

La UI de comparacion pasa a exponer tres acciones con semantica distinta:

* `Refrescar snapshot`
  * recarga snapshot persistido e historial
  * no recalcula matching
* `Recomparar pendientes`
  * ejecuta la ruta incremental ordinaria
  * recalcula solo lo que el motor considera pendiente o invalidado
* `Recomparar todo`
  * fuerza recomputacion completa
  * ignora el ahorro incremental del snapshot anterior

Ademas, la pantalla muestra estado visible del snapshot:

* `Snapshot cargado`
* `Snapshot obsoleto`
* `Recomparando pendientes`
* `Recalculando todo`

Si el snapshot queda obsoleto por un cambio conocido, la UI muestra tambien el motivo textual.

## Consecuencias

* el usuario ya no confunde una accion barata con una tarea costosa
* la recomputacion completa queda disponible, pero como accion explicita y separada
* la obsolescencia del snapshot deja trazabilidad visible en la propia pantalla
