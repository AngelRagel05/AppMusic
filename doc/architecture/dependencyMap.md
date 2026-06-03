# Mapa de dependencias

## Reglas permitidas

```txt
presentation -> application
application -> domain
infrastructure -> domain
infrastructure -> application contracts
bootstrap -> presentation + application + infrastructure
workers -> application + infrastructure
shared -> dependencias transversales sin negocio
```

## Reglas prohibidas

```txt
presentation -> infrastructure
domain -> infrastructure
domain -> presentation
application -> presentation
widgets -> SQLAlchemy / pygame / yt-dlp / Mutagen / FFmpeg
```

## Excepcion controlada

`bootstrap/` actua como composition root y puede conocer varias capas a la vez porque su trabajo es cablearlas.

## Refuerzo automatico

Estas reglas se refuerzan con:

* [layerDependencyRules.md](./adr/layerDependencyRules.md)
* [tests/unit/testDependencyRules.py](../../tests/unit/testDependencyRules.py)

La ADR historica asociada vive en `doc/architecture/adr/layerDependencyRules.md`.
