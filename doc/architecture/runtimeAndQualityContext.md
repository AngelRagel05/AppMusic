# Contexto de Runtime y Calidad

## Objetivo

Unificar la documentacion sobre bootstrap, workers, seguridad de hilos, validacion rapida y testing.

## Bootstrap

El composition root vive en `bootstrap/` y es responsable de:

* crear adaptadores
* instanciar use cases
* construir viewmodels
* cablear controllers y ventanas

## Workers y concurrencia

Las operaciones pesadas deben ejecutarse fuera del hilo principal.

Casos tipicos:

* escaneo de biblioteca local
* recomparacion de playlist
* operaciones externas de descarga o metadata

Reglas:

* los workers no actualizan widgets directamente
* emiten resultados hacia la capa de presentacion
* la persistencia compartida entre hilos debe ser segura

## Testing

Estructura:

```txt
tests/
├─ unit/
├─ integration/
└─ e2e/
```

### `unit`

Cubren:

* validadores
* helpers
* servicios de dominio
* use cases con dobles simples
* viewmodels y controllers con spies

### `integration`

Cubren:

* SQLAlchemy
* bootstrap de base de datos
* repositorios concretos
* regresiones funcionales de comparacion

### `e2e`

Reservado para:

* arranque automatizado
* flujos multi-capa

## Verificacion rapida

El proyecto dispone de:

* `python scripts/verifyFront.py`
* `.\runFrontChecks.ps1` en Windows

## Regresiones de comparacion

Las regresiones del matching deben respetar el flujo definido en:

* [comparisonContext.md](./comparisonContext.md)

## Otras politicas documentales vivas

* [../pythonBytecodePolicy.md](../pythonBytecodePolicy.md)
* [../listCrudActions.md](../listCrudActions.md)

