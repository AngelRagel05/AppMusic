# ADR: Arranque de ventana en pantalla completa

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La aplicacion se usa como escritorio principal de trabajo y debe abrir con la mayor superficie posible desde el arranque.

Hasta ahora el arranque usaba un tamaño base grande y un intento de ventana maximizada, pero no una politica explicita de pantalla completa por defecto.

## Decision

La ventana principal arranca en pantalla completa por defecto desde la configuracion centralizada de `windowStyler.py`.

La politica queda asi:

* primero se intenta `fullscreen`
* si el entorno no lo soporta correctamente, se mantiene tambien el fallback existente de ventana maximizada

## Consecuencias

Ventajas:

* la app abre lista para uso intensivo sin ajuste manual
* la decision queda centralizada en un unico punto de estilo de ventana

Coste:

* algunos entornos pueden preferir solo maximizado, por lo que se mantiene fallback compatible
