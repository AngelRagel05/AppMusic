# Clasificacion de tests por nivel

## Estado

Aprobado.

## Estructura

```txt
tests/
├─ unit/
├─ integration/
└─ e2e/
```

## Criterios

### unit

Incluye pruebas de:

* `domain`
* `application`
* `shared`
* `viewmodels`
* `controllers` con spies o dobles simples
* reglas arquitectonicas basadas en analisis de imports

No deben requerir infraestructura real.

### integration

Incluye pruebas de:

* SQLAlchemy
* modelos ORM
* bootstrap de base de datos
* repositorios concretos
* adaptadores reales de infraestructura

Pueden usar SQLite en memoria u otros dobles tecnicos de integracion.

### e2e

Reservado para:

* arranque automatizado de la aplicacion
* escenarios completos de usuario
* recorridos funcionales de varias capas encadenadas

Actualmente queda preparado pero sin tests reales para no sobrerrotular pruebas existentes.

## Decision aplicada

Se han movido los tests actuales manteniendo su comportamiento:

* `tests/unit/` contiene validadores, use cases, support helpers, viewmodels, controllers, settings y reglas de dependencia
* `tests/integration/` contiene bootstrap, modelos y repositorios SQLAlchemy
* `tests/e2e/` queda inicializado con una nota de uso futuro
