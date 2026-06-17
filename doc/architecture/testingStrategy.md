# Estrategia de testing

## Estructura

```txt
tests/
├─ unit/
├─ integration/
└─ e2e/
```

## unit

Cubren:

* validadores
* use cases
* helpers compartidos
* settings
* viewmodels
* controllers con spies
* reglas arquitectonicas por analisis de imports
* helpers o mapeos pequeños sin infraestructura

## integration

Cubren:

* modelos SQLAlchemy
* bootstrap de base de datos
* repositorios concretos
* persistencia real con SQLite en memoria
* regresiones funcionales de comparacion con casos reales representativos

## e2e

Reservado para:

* arranque automatizado de la aplicacion
* recorridos funcionales completos
* escenarios de usuario multi-capa

Actualmente queda preparado pero sin suites reales.

## Verificacion rapida de front

El proyecto dispone de un comando unico para validar la capa de front sin arrancar una ventana real:

* `python scripts/verifyFront.py`
* en Windows tambien: `.\runFrontChecks.ps1`

Ese comando ejecuta:

* `compileall` sobre `app/presentation`, workers ligados a UI y bootstrap de presentacion
* `ruff` solo con errores graves (`E9`, `F63`, `F7`, `F82`)
* `pytest` sobre controllers, viewmodels y helpers de comparacion/presentacion

La estrategia evita depender de un display grafico en CI, por lo que no intenta abrir `Tk` real ni hacer pruebas visuales end-to-end.

## Criterio de alcance

* si una prueba necesita dobles simples y no toca recursos reales, pertenece a `unit/`
* si verifica SQLAlchemy, SQLite, repositorios o adaptadores concretos, pertenece a `integration/`
* si recorre el arranque o un flujo de usuario multi-capa de punta a punta, pertenece a `e2e/`

## Documento historico relacionado

* `doc/architecture/adr/testLevelsClassification.md`
* `doc/architecture/adr/comparisonObservabilityAndPerformanceValidation.md`
