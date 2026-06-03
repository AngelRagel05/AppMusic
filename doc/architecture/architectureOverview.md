# Arquitectura general

## Objetivo

El proyecto sigue una arquitectura limpia ligera con separacion clara entre interfaz, casos de uso, dominio e infraestructura.

La estructura actual de referencia es:

```txt
app/
├─ bootstrap/
├─ presentation/
├─ application/
├─ domain/
├─ infrastructure/
├─ shared/
├─ workers/
└─ config/
```

## Capas

### `presentation/`

Responsable de:

* ventanas
* widgets
* viewmodels
* controllers de UI
* estilos

No debe contener reglas de negocio pesadas ni acceso directo a infraestructura.

### `application/`

Responsable de:

* casos de uso
* DTOs
* validadores de entrada

Orquesta acciones del sistema sin conocer detalles de UI ni implementaciones concretas de infraestructura.

### `domain/`

Responsable de:

* entidades
* acciones de dominio
* servicios de dominio
* contratos de repositorio

No depende de frameworks ni adaptadores externos.

### `infrastructure/`

Responsable de:

* persistencia
* integraciones externas
* adaptadores tecnicos

Contiene implementaciones concretas de contratos definidos en capas superiores.

### `shared/`

Responsable de:

* utilidades transversales
* excepciones compartidas
* constantes comunes

No debe contener logica de dominio.

### `bootstrap/`

Responsable de:

* composition root
* construccion y cableado de dependencias

## Flujo principal

```txt
UI -> ViewModel/Controller -> UseCase -> Domain -> Repository/Infrastructure
```

## Documentos relacionados

* [dependencyMap.md](./dependencyMap.md)
* [domainModulesOverview.md](./domainModulesOverview.md)
* [presentationStructure.md](./presentationStructure.md)
* [testingStrategy.md](./testingStrategy.md)
* [externalIntegrations.md](./externalIntegrations.md)
