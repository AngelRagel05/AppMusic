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

* [target_architecture_and_layer_map.md](./target_architecture_and_layer_map.md)
* [presentation_ui_pure_structure.md](./presentation_ui_pure_structure.md)
* [infrastructure_adapter_reorganization.md](./infrastructure_adapter_reorganization.md)
* [composition_root_modular_factories.md](./composition_root_modular_factories.md)
