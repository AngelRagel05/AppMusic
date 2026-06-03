# Reglas de dependencia entre capas

## Estado

Aprobado.

## Objetivo

Fijar reglas de dependencia simples y verificables para evitar acoplamientos entre capas que degraden la arquitectura.

## Reglas permitidas

```txt
presentation -> application
application -> domain
infrastructure -> domain
infrastructure -> application contracts
bootstrap -> application / infrastructure / presentation
shared -> utilidades y constantes transversales
```

## Reglas prohibidas

```txt
presentation -> infrastructure
domain -> infrastructure
widgets -> SQLAlchemy / pygame / yt-dlp / Mutagen / FFmpeg
```

## Notas

* `bootstrap/` es el composition root y queda exento de las restricciones normales entre capas porque su trabajo es cablear dependencias.
* `shared/` no es una capa de negocio; solo aloja utilidades, constantes y excepciones transversales sin dominio.
* `presentation/widgets/` debe seguir siendo visual y reutilizable. No puede hablar con persistencia ni con integraciones externas.

## Verificacion

Estas reglas quedan respaldadas por `tests/unit/testDependencyRules.py`, que revisa imports de forma automatica para:

* impedir `presentation -> infrastructure`
* impedir `domain -> infrastructure`
* impedir imports de paquetes de integracion externa dentro de `presentation/widgets`
