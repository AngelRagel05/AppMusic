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

La implementacion visual debe usar un widget tabular real con columnas persistentes compartidas por cabecera y filas.

Queda descartado renderizar cada fila como un `Frame` independiente simulando columnas, porque eso rompe la alineacion y degrada la experiencia de escritorio.

La caja de busqueda de esta pantalla se orienta a buscar dentro de resultados por titulo o artista, tanto de playlist como de coincidencia local.

La estetica final de esta pantalla debe priorizar densidad de informacion y compacidad de escritorio:

* filas de una sola linea
* detalle inferior compacto
* seleccion sutil
* historico no invasivo cuando esta vacio

Cada resultado abre un detalle dedicado en modal al pulsar su fila.

El detalle modal muestra:

* disponibilidad detectada
* score
* coincidencia local
* revision
* cancion local enlazada cuando existe
* motivo resumido y detalle textual de comparacion

## Consecuencias

Ventajas:

* mejora la lectura masiva de resultados
* hace mas visibles faltantes y coincidencias dudosas
* mantiene busqueda, filtro y paginacion sin cambiar el flujo del controlador

Costes:

* la vista de canciones locales deja de ser el foco principal dentro de esta pantalla
* la tabla requiere formateo especifico de filas dentro de `presentation/features/comparison`
* el estilo oscuro de la tabla necesita configuracion explicita del widget nativo elegido

## Implementacion

La logica de formateo de filas se centraliza en `comparisonTableRowViewData.py` para poder probar la presentacion tabular sin depender de widgets `CustomTkinter`.

La vista de resultados usa un control tabular real estilizado en oscuro para garantizar:

* cabecera y filas alineadas
* altura de fila constante
* seleccion compacta
* scroll vertical estable
