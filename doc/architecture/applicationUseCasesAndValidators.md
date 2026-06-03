# Reorganizacion de application por modulo y validacion

## Estado

Aprobado.

## Contexto

La capa `app/application/` habia crecido con dos problemas:

* los use cases estaban en un espacio plano aunque ya existian modulos claros del dominio
* varias validaciones de entrada estaban duplicadas entre use cases del mismo contexto

Ademas, debiamos reforzar que los use cases mantuvieran un contrato coherente con `execute(...)` y sin dependencia directa de UI.

## Decision

Se reorganiza `app/application/use_cases/` en submodulos por contexto:

```txt
app/application/use_cases/
├─ library/
├─ playlists/
├─ filters/
└─ system/
```

Se introduce `app/application/validators/` para validacion compartida de entrada:

```txt
app/application/validators/
├─ library/
├─ playlists/
└─ filters/
```

Reglas adoptadas:

* cada use case expone `execute(...)` como punto de entrada principal
* `presentation` depende de `app.application.use_cases` como API publica, no de archivos internos concretos
* la validacion repetida de ids, rutas y urls se centraliza en `validators/`
* los use cases no dependen de UI
* los use cases no deben importar implementaciones concretas de infraestructura; cuando necesitan colaboracion externa deben depender de una abstraccion o protocolo

## Consecuencias

Ventajas:

* menor duplicacion entre use cases
* imports mas estables para `presentation` y `tests`
* mejor alineacion con SRP y DIP
* crecimiento futuro mas claro por modulo

Coste:

* la estructura interna de `application` gana subcarpetas y requiere mantener `__init__.py` como API de reexportacion
