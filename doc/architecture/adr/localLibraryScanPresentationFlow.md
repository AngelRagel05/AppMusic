# ADR: Flujo de escaneo en presentation

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La UI ya tenia dos puntos visibles para iniciar el escaneo de biblioteca:

* la accion `Sincronizar biblioteca` en `localLibrary`
* el boton de escaneo en `overview`

Hacia falta conectarlos al mismo flujo sin meter logica de escaneo en widgets ni concentrarla en el controller.

## Decision

Se introduce `LocalLibraryScanViewModel` como pieza de coordinacion de presentacion para el escaneo.

El reparto queda asi:

* `overview` delega en `AppShellController`, que redirige a `localLibrary` y dispara el mismo flujo
* `LocalLibraryController` solo conecta eventos y renderiza `LocalLibraryScanFeedback`
* `LocalLibraryScanViewModel` coordina el arranque del worker y transforma el resultado en feedback de presentacion
* `ScanLocalFolderWorker` ejecuta el caso de uso fuera del hilo principal

## Consecuencias

Ventajas:

* la accion principal de `localLibrary` expresa mejor que el flujo detecta altas, refresca cambios y marca bajas
* los puntos visibles de entrada reutilizan el mismo flujo
* el contador de canciones y la ultima accion se actualizan desde un feedback unico de presentacion
* la logica de escaneo no vive en widgets
* la v1 ya expone el minimo de resultado pedido: exito o error, MP3 detectados y canciones registradas

Coste:

* se introduce un viewmodel adicional especifico para esta interaccion
