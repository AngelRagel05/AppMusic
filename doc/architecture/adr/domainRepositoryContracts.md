# ADR: Contratos de repositorio en `domain/repositories`

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

Los contratos de persistencia del dominio estaban ubicados en `app/domain/services/`.

Aunque funcionaba a nivel tecnico, el lenguaje quedaba impreciso:

* `services/` mezclaba contratos de repositorio con una carpeta reservada conceptualmente para logica de dominio
* el dominio no diferenciaba con claridad entre servicio de dominio y puerto de persistencia

## Decision

Se mueven los contratos de repositorio a:

```txt
app/domain/repositories/
```

Contenido actual:

* `baseRepository.py`
* `ignoredTermRepository.py`
* `localFolderRepository.py`
* `youtubePlaylistRepository.py`

`app/domain/services/` queda reservado para logica de dominio real cuando exista.

## Consecuencias

Ventajas:

* el lenguaje del dominio queda mas limpio
* los puertos de persistencia se identifican como repositorios y no como servicios
* la estructura se acerca mas a DDD light sin sobreingenieria

Costes:

* hay que actualizar imports en `application`, `infrastructure` y tests

## Regla operativa

Si una abstraccion representa acceso a colecciones persistentes o recuperacion/guardado de entidades, debe vivir en `domain/repositories/`.

Si encapsula una regla o coordinacion propia del negocio, puede vivir en `domain/services/`.
