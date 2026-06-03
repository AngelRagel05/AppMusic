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

## e2e

Reservado para:

* arranque automatizado de la aplicacion
* recorridos funcionales completos
* escenarios de usuario multi-capa

Actualmente queda preparado pero sin suites reales.

## Criterio de alcance

* si una prueba necesita dobles simples y no toca recursos reales, pertenece a `unit/`
* si verifica SQLAlchemy, SQLite, repositorios o adaptadores concretos, pertenece a `integration/`
* si recorre el arranque o un flujo de usuario multi-capa de punta a punta, pertenece a `e2e/`

## Documento historico relacionado

* `doc/architecture/adr/testLevelsClassification.md`
