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

## integration

Cubren:

* modelos SQLAlchemy
* bootstrap de base de datos
* repositorios concretos
* persistencia real con SQLite en memoria

## e2e

Reservado para:

* arranque automatizado de la aplicacion
* recorridos funcionales completos
* escenarios de usuario multi-capa

Actualmente queda preparado pero sin suites reales.

## Documento relacionado

* [testLevelsClassification.md](./testLevelsClassification.md)
