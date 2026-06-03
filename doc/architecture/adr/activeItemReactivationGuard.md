# ADR: Bloqueo de reactivacion de elementos ya activos

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

Las features `localLibrary` y `youtubePlaylists` permiten activar una carpeta local o una playlist guardada.

Cuando un elemento ya estaba activo, la UI seguia ofreciendo la accion de activarlo otra vez y el controller podia volver a disparar el flujo de activacion.

Eso añade ruido de UX y llamadas innecesarias a casos de uso sin aportar ningun cambio de estado.

## Decision

Se bloquea la reactivacion de elementos ya activos en dos niveles:

* la UI deshabilita el boton `Activar` en la fila del elemento activo
* el controller valida el estado actual antes de llamar al viewmodel y rechaza la accion si el elemento ya esta activo

## Consecuencias

Ventajas:

* evita acciones redundantes
* mejora claridad visual de la accion disponible
* reduce llamadas innecesarias a la capa de aplicacion

Coste:

* el estado de cada fila debe reflejar correctamente si el elemento esta activo
