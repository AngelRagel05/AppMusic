# ADR: Worker para escaneo de biblioteca local

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

El escaneo de filesystem puede bloquear la interfaz si se ejecuta directamente desde el controller o desde widgets de Tkinter.

Ademas, la capa `presentation` ya expone acciones de `Escanear biblioteca`, pero necesitaba una pieza dedicada para:

* ejecutar el caso de uso fuera del hilo principal
* devolver el resultado al controller
* asegurar que la UI solo se actualiza desde el hilo principal

## Decision

Se introduce `ScanLocalFolderWorker` en `app/workers/scanLocalFolderWorker.py`.

El worker:

* ejecuta `ScanLocalFolderUseCase` en un `Thread` en segundo plano
* entrega `ScanLocalFolderResultDto` al controller mediante callbacks
* agenda esos callbacks en el hilo principal usando un scheduler inyectado

El worker no:

* toca widgets directamente
* conoce detalles de `CustomTkinter`
* persiste por su cuenta fuera del caso de uso

## Consecuencias

Ventajas:

* el escaneo no bloquea la UI
* el controller conserva el control del feedback visual
* la actualizacion de widgets queda confinada al hilo principal

Costes:

* se introduce una pieza mas en el flujo de escaneo
* el wiring en `bootstrap` y `presentation` crece ligeramente
