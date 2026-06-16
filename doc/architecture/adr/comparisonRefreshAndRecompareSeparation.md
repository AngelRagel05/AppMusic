# Comparison Refresh And Recompare Separation

## Contexto

La pantalla `Comparacion` usaba un unico gesto de `refresh` para dos cosas distintas:

* recargar el snapshot persistido ya guardado
* disparar una recomparacion completa de varios minutos

Eso hacia que la UI ocultara el coste real de la accion y que el usuario pagara una recomputacion total cuando solo queria refrescar la vista.

## Decision

Se separan las acciones de presentacion:

* `Refrescar snapshot`
  * recarga desde BBDD el ultimo snapshot persistido y su historico
  * no dispara `CompareYoutubePlaylistWithLocalLibraryUseCase`
* `Recomparar`
  * ejecuta el worker de comparacion
  * genera un snapshot nuevo y actualiza el historico

El `LibraryComparisonViewModel` pasa a modelar explicitamente el estado del snapshot:

* `fresh`
* `stale`
* `recomputing`

## Reglas operativas

* `load()` prioriza snapshot persistido y nunca recomputa por si solo
* `invalidateComparison()` solo marca `stale`
* `refreshPersistedComparison()` puede recargar snapshot sin limpiar el estado `stale`
* `requestRecomparison()` es la unica ruta que entra en `LoadLibraryComparisonWorker`

## Consecuencias

* el usuario ve cuando esta consultando snapshot persistido
* el coste de la recomparacion queda visible y confirmado
* refresh y recomparacion dejan de compartir semantica
* los tests pueden proteger que un refresh de vista no arranque trabajo pesado
