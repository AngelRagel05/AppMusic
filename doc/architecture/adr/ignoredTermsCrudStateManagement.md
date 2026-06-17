# CRUD y estado activo de terminos ignorados

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Objetivo

Completar la gestion de terminos ignorados con un CRUD usable desde la UI y soporte explicito
de activacion o desactivacion sin borrar datos.

## Decision

La gestion de terminos ignorados queda soportada por:

* listado completo desde `IgnoredTermsViewModel`
* alta y edicion mediante formulario superior
* cambio de estado activo con un caso de uso dedicado `SetIgnoredTermActiveStateUseCase`
* eliminacion fisica solo cuando el usuario la solicita expresamente
* unicidad persistente por `term + scope + language`

Ademas, cualquier cambio en terminos ignorados invalida el snapshot de comparacion cargado
para obligar a recomputar con la configuracion vigente.

## Motivo tecnico

Separar el cambio de estado en un caso de uso propio evita mezclar semanticas distintas dentro
de `updateIgnoredTermUseCase` y mantiene un contrato claro entre presentacion, aplicacion y
repositorio.

La invalidez del snapshot evita mostrar como vigente una comparacion calculada con otra
configuracion de terminos.

## Alcance

No se cambia el esquema de base de datos porque `ignored_term` ya dispone de `is_active` y
de restriccion unica compuesta.
