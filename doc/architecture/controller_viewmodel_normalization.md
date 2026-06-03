# ADR: Normalizacion del patron controller/viewmodel

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

Las features de presentacion con operaciones tipo CRUD compartian un patron casi identico:

* cargar lista
* cargar activo si aplica
* editar por id
* eliminar por id
* volver a consultar la lista para localizar elementos concretos

Ese enfoque duplicaba logica entre controllers y forzaba consultas repetidas al mismo estado de presentacion.

## Decision

Se normaliza el reparto asi:

* el controller coordina flujo, mensajes y navegacion
* el viewmodel sigue siendo un adaptador fino a use cases
* el viewmodel mantiene cache de coleccion y, cuando aplica, del elemento activo
* la busqueda por id se resuelve desde el viewmodel con estado cacheado

## Regla aplicada

Los viewmodels de features CRUD exponen un patron comun:

* `refreshState()`
* `load_*()` para leer cache
* `find_*_by_id()` para localizar elementos sin recargar listas
* metodos de mutacion que refrescan cache tras ejecutar el use case

## Consecuencias

Ventajas:

* menos repeticion entre controllers
* menos consultas redundantes a listas ya cargadas
* los controllers dejan de buscar elementos recorriendo listas cada vez
* el estado de presentacion queda mas consistente tras create/update/delete/activate

Costes:

* el viewmodel asume una responsabilidad ligera de cache de presentacion

## Nota

La cache vive solo en `presentation`.

No sustituye reglas de dominio ni convierte el viewmodel en capa de negocio.
