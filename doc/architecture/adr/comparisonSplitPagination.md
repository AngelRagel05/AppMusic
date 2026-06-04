# Comparison Split Pagination

## Contexto

La pantalla `Comparacion` mostraba de golpe todas las canciones locales y todos los items importados de la playlist activa.

Con bibliotecas grandes eso bloqueaba el hilo principal de Tkinter al crear demasiados widgets de una sola vez.

## Decision

La pantalla `Comparacion` pagina cada columna por separado.

Reglas aplicadas:

* tamano inicial de pagina: `25`
* el usuario puede cambiarlo desde la interfaz
* cada columna mantiene su propia pagina actual
* solo se renderiza la pagina visible
* el render de cada pagina se hace por tandas pequenas usando `after(0, ...)`

La logica de paginacion se mueve a `ComparisonPaginationState` fuera de `ui/` para no mezclar estado reutilizable con widgets.

## Consecuencias

* la pantalla deja de intentar construir miles de filas de una sola vez
* la navegacion entre paginas es predecible y barata
* el cambio de tamano de pagina conserva aproximadamente el punto visible actual
* la UI sigue siendo responsiva incluso con colecciones grandes
