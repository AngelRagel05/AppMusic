# Estructura vigente de presentation

## Objetivo

Definir una unica referencia canónica para la organizacion de `app/presentation/`.

Este documento sustituye como guia viva a documentacion anterior basada en rutas legacy hoy superadas.

## Estructura canónica

```txt
app/presentation/
├─ features/
│  └─ <feature>/
│     ├─ controller/
│     └─ ui/
├─ windows/
├─ dialogs/
├─ widgets/
├─ viewmodels/
│  └─ <feature>/
└─ styles/
```

## Reparto de responsabilidades

### `windows/`

Contiene la estructura global del escritorio:

* `MainWindow`
* `AppShell`
* sidebar
* navegacion y composicion global

No debe contener logica funcional propia de una feature.

### `dialogs/`

Contiene dialogos modales y ventanas auxiliares reutilizables o especificas cuando existan.

### `widgets/`

Contiene componentes visuales reutilizables entre varias features o entre features y shell.

Ejemplos tipicos:

* `PageHeader`
* `StatusBadge`
* `StatCard`
* `DataTable`

Si un componente solo sirve a una feature, no debe vivir aqui.

### `viewmodels/`

Agrupa el estado y la coordinacion ligera de UI por feature.

Los viewmodels:

* llaman a use cases
* mantienen cache o estado de presentacion
* no implementan reglas de negocio pesadas
* no deben hablar directamente con infraestructura

### `styles/`

Centraliza:

* paleta
* factories de widgets
* soporte visual comun
* helpers de ventana

Toda referencia viva a `uiTheme/` queda obsoleta.

### `features/`

Cada feature agrupa su UI especifica y sus controladores:

```txt
<feature>/
├─ controller/
└─ ui/
```

Las features canonicas actuales son:

* `overview`
* `localLibrary`
* `youtubePlaylists`
* `ignoredTerms`

## MVC ligero en presentation

### View

La vista:

* crea widgets
* define layout
* renderiza estado visual
* expone metodos de lectura o actualizacion de su propio arbol visual

No debe:

* ejecutar casos de uso
* acceder a infraestructura
* decidir reglas de negocio

### Controller

El controller:

* conecta eventos de la vista
* decide el flujo de interaccion
* llama a viewmodels
* actualiza la vista con el resultado

### Model en presentation

El papel de modelo en `presentation` se apoya en:

* `viewmodels/`
* DTOs de `application`
* casos de uso como frontera de accion

No se introducen entidades de dominio ni detalles ORM dentro de `presentation`.

## Reglas de componentes visuales

Cada componente visual debe vivir en su propia carpeta con su modulo principal:

```txt
componentName/
└─ componentName.py
```

Reglas:

* cuando varios componentes pertenecen a una misma pantalla, se agrupan bajo la carpeta padre de la feature
* los imports deben apuntar al modulo real y no depender de reexports innecesarios
* `__init__.py` solo se mantiene cuando aporta una API de paquete real
* los helpers no visuales no deben vivir dentro de `ui/`

## Convencion de nombres

* archivos y carpetas del proyecto en `camelCase`
* clases en `PascalCase`
* solo quedan fuera los nombres generados por Python o impuestos por tooling externo, como `__init__.py`, `__pycache__/` o `.pyc`

## Regla de vigencia

La estructura actual del repositorio es la unica referencia viva.

Las referencias a rutas o estructuras legacy solo pueden mantenerse en ADRs historicas para explicar fases anteriores.

## Documentos historicos relacionados

* `doc/architecture/adr/featureModularPresentationTkinter.md`
* `doc/architecture/adr/presentationFeatureReorganization.md`
* `doc/architecture/adr/presentationUiPureStructure.md`
* `doc/architecture/adr/sharedUiCleanup.md`
* `doc/architecture/adr/presentationMvc.md`
* `doc/architecture/adr/componentStructure.md`
