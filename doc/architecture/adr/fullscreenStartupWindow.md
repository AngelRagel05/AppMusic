# ADR: Arranque de ventana maximizada por defecto

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La aplicacion se usa como escritorio principal de trabajo y debe abrir con la mayor superficie posible desde el arranque.

La necesidad es ocupar la pantalla desde el inicio sin entrar en modo fullscreen exclusivo.

## Decision

La ventana principal arranca maximizada por defecto desde la configuracion centralizada de `windowStyler.py`.

La politica queda asi:

* se mantiene un tamaño base razonable
* se intenta abrir la ventana en estado maximizado con `zoomed`
* no se usa modo `fullscreen`

## Consecuencias

Ventajas:

* la app abre lista para uso intensivo sin ajuste manual
* se evita el comportamiento mas invasivo del fullscreen real
* la decision queda centralizada en un unico punto de estilo de ventana

Coste:

* el resultado visual depende del soporte del entorno para `zoomed`
