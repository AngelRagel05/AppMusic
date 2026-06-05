# Comparison Feedback And Filters

## Contexto

La pantalla `Comparacion` ya mostraba resultados de matching, pero faltaban dos piezas de uso diario:

* un resumen visible arriba
* un filtro rapido por estado

Sin eso, la lectura de resultados era peor cuando la playlist tenia muchos items.

## Decision

Se anaden dos elementos a la feature:

* resumen superior con:
  * encontradas
  * faltan
  * posibles coincidencias
* filtro visual por estado:
  * todos
  * encontradas
  * faltan
  * posibles coincidencias

La logica de filtro se extrae a `comparisonResultFilter.py` para no mezclarla con el render de widgets.

La paginacion existente se mantiene y se aplica sobre la lista ya filtrada.

## Consecuencias

* el usuario puede centrarse rapidamente en faltantes o coincidencias dudosas
* el resumen queda visible sin recorrer la lista completa
* no se vuelve a renderizar toda la coleccion, solo la pagina filtrada activa
