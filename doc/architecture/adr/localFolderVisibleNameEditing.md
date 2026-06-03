# ADR: Edicion explicita del nombre visible de bibliotecas locales

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La entidad `LocalFolder` ya persistia `display_name`, pero la aplicacion solo lo derivaba desde el nombre de la ruta.

Eso permitia cambiar el nombre visible solo de forma indirecta al mover o elegir otra carpeta, pero no editarlo como dato de negocio de presentacion.

## Decision

La biblioteca local admite un nombre visible editable de forma explicita.

La politica queda asi:

* la UI expone un campo de nombre visible
* `create` y `update` aceptan `display_name`
* si el usuario lo deja vacio, se mantiene el fallback automatico al nombre de la carpeta

## Consecuencias

Ventajas:

* el usuario puede nombrar sus bibliotecas con un alias util sin depender del nombre fisico de la carpeta
* se conserva compatibilidad con el comportamiento anterior cuando no se informa un alias

Coste:

* el formulario de biblioteca local añade un campo mas
