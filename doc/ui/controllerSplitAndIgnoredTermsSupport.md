# Refactor de controladores y soporte de terminos ignorados

## Objetivo

Reducir duplicidad y acoplamiento sin cambiar el comportamiento actual de la UI.

## Decision

Se divide `MainWindowController` en controladores por area:

* `LocalLibrariesController`
* `YoutubePlaylistsController`
* `IgnoredTermsController`

`MainWindowController` queda como coordinador de alto nivel para inicializacion y estado compartido del dashboard.

Ademas, la logica comun de `normalize`, `validate` y `map` del flujo de terminos ignorados se centraliza en `app/application/ignoredTermSupport.py`.

## Motivo tecnico

Antes del cambio habia duplicidad en:

* validacion y normalizacion de `term`, `scope` y `language`
* mapeo de entidad a `IgnoredTermDto`
* orquestacion CRUD repetida dentro de un unico controlador de ventana

Con este ajuste:

* cada controlador tiene una responsabilidad mas clara
* los use cases de terminos ignorados comparten reglas coherentes
* se reduce el riesgo de divergencia al cambiar validaciones o transformaciones

## Alcance

No se cambia el comportamiento funcional ni el contrato de los viewmodels.

No se introduce una jerarquia generica de controladores para evitar sobreingenieria.
