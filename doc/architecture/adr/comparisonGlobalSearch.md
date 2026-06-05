# Comparison Global Search

## Contexto

La vista de comparacion ya mostraba dos listas grandes:

* canciones de biblioteca local
* resultados de comparacion

El usuario necesitaba encontrar texto en ambas sin tener que filtrar una por una ni lanzar acciones manuales.

## Decision

Se añade un buscador global con filtrado en vivo.

Mientras el usuario escribe:

* se filtran las canciones locales
* se filtran los resultados de comparacion
* el filtro de estado de comparacion sigue aplicandose solo a la lista de resultados

La busqueda usa coincidencia textual simple por tokens sobre metadata ya disponible en memoria.

## Consecuencias

* la interaccion es inmediata y no requiere volver a pulsar botones
* no se añade coste de infraestructura ni nuevas consultas
* el filtrado sigue siendo barato porque trabaja sobre listas ya cargadas en la vista
