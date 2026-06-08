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
* texto explicito por item para indicar si existe en local, si no existe o si solo hay posible coincidencia

La logica de filtro se extrae a `comparisonResultFilter.py` para no mezclarla con el render de widgets.

La logica textual de disponibilidad por item se extrae a `comparisonAvailabilitySummary.py` para mantener la UI de `comparisonSplitSection` centrada en render.

Cuando el filtro activo es `Todos`, la vista prioriza visualmente:

* faltan
* posibles coincidencias
* encontradas

Ademas, las filas `Falta` se resaltan con mas contraste para que destaquen al recorrer la lista.
Las filas `Posible coincidencia` tambien quedan resaltadas y muestran el aviso `Revisar manualmente` para que las coincidencias dudosas se detecten rapido.

La paginacion existente se mantiene y se aplica sobre la lista ya filtrada.

## Consecuencias

* el usuario puede centrarse rapidamente en faltantes o coincidencias dudosas
* el resumen queda visible sin recorrer la lista completa
* no se vuelve a renderizar toda la coleccion, solo la pagina filtrada activa
* cada item de playlist deja visible de forma directa si existe o no en la biblioteca local
* en la vista general, las canciones faltantes aparecen antes y se identifican mas rapido
* las coincidencias dudosas quedan visibles como elementos que requieren revision manual
