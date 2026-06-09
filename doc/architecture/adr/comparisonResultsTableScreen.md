# ADR: Pantalla tabular para resultados de comparacion

## Contexto

La comparacion mostraba los resultados como una lista compacta dentro de la pantalla de comparacion.

Ese formato funcionaba para pocas filas, pero hacia mas lenta la revision cuando el usuario queria:

* recorrer rapidamente muchos resultados
* detectar faltantes y posibles coincidencias en bloque
* comparar de un vistazo los datos de playlist frente a la coincidencia local

## Decision

La pantalla principal de comparacion pasa a mostrar una tabla paginada de resultados como vista dominante.

La tabla expone estas columnas:

* estado
* titulo de playlist
* artista de playlist
* coincidencia local
* score
* revision

La caja de busqueda de esta pantalla se orienta a buscar dentro de resultados por titulo o artista, tanto de playlist como de coincidencia local.

Ademas, la fila seleccionada muestra un panel de detalle inferior con:

* disponibilidad detectada
* score
* cancion local enlazada cuando existe
* motivo resumido de comparacion

Cada resultado puede abrir ademas un detalle dedicado mediante doble clic en la fila o usando la accion `Abrir detalle` del panel inferior.

## Consecuencias

Ventajas:

* mejora la lectura masiva de resultados
* hace mas visibles faltantes y coincidencias dudosas
* mantiene busqueda, filtro y paginacion sin cambiar el flujo del controlador

Costes:

* la vista de canciones locales deja de ser el foco principal dentro de esta pantalla
* la tabla requiere formateo especifico de filas dentro de `presentation/features/comparison`

## Implementacion

La logica de formateo de filas se centraliza en `comparisonTableRowViewData.py` para poder probar la presentacion tabular sin depender de widgets `CustomTkinter`.
