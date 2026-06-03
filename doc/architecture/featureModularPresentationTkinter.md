# ADR: Feature Modular Presentation for Tkinter

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

Tras la migracion de `PySide6` a `Tkinter`/`CustomTkinter`, la capa `presentation/` ha quedado con una estructura mixta:

* parte del codigo se organiza por tipo tecnico global (`controllers/`, `viewmodels/`, `uiTheme/`)
* parte del codigo ya se organiza por pantalla y feature dentro de `ui/`

Esta mezcla dificulta:

* localizar rapidamente el codigo de una feature concreta
* mantener una separacion clara entre shell de aplicacion, elementos compartidos y modulos funcionales
* escalar la UI sin aumentar acoplamiento entre paginas, layout global y controladores

El proyecto ademas sigue una arquitectura limpia ligera y el criterio de `AGENTS.md` exige separar responsabilidades, aplicar SOLID con pragmatismo y mantener la UI fraccionada en carpetas coherentes.

## Decision

La capa `presentation/` pasa oficialmente a organizarse con el criterio:

```txt
presentation/
├─ shell/
├─ shared/
└─ features/
```

### `shell/`

Contiene el armazon global de la aplicacion:

* ventana principal
* layout principal
* navegacion entre pantallas
* composicion general de la UI

`shell/` no debe contener logica funcional propia de una feature.

### `shared/`

Contiene piezas reutilizables de presentacion:

* tema visual
* factories de widgets
* senales/eventos de UI
* componentes comunes
* helpers visuales transversales

`shared/` no debe contener comportamiento especifico de una feature.

### `features/`

Contiene los modulos funcionales de presentacion. Cada feature agrupa su propio codigo de UI y coordinacion.

Estructura objetivo:

```txt
presentation/
└─ features/
   ├─ overview/
   ├─ localLibrary/
   ├─ youtubePlaylists/
   └─ ignoredTerms/
```

Cada feature podra contener, segun necesidad real:

```txt
featureName/
├─ ui/
├─ controller/
└─ viewmodel/
```

No es obligatorio crear subcarpetas vacias si una feature todavia es pequena, pero el criterio de agrupacion sigue siendo por feature y no por tipo tecnico global.

## Naming oficial de features

Se fijan estos nombres canonicos para carpetas y referencias documentales de la capa de presentacion:

* `overview`
* `localLibrary`
* `youtubePlaylists`
* `ignoredTerms`

Reglas:

* usar `camelCase` en carpetas y archivos Python de `presentation/`
* no mezclar variantes como `localLibraries`, `libraryLocal`, `playlistYouTube` o `filters` cuando se hable de la feature
* si una vista representa navegacion o shell global, no debe recibir nombre de feature

## Consecuencias

Ventajas:

* cada feature queda encapsulada y es mas facil de localizar
* el shell deja de depender de detalles internos de cada pantalla
* la capa compartida de UI queda separada de la funcional
* la arquitectura encaja mejor con MVC ligero, DDD light y crecimiento incremental

Costes:

* sera necesario mover carpetas y ajustar imports
* algunas clases actuales tendran nombres o ubicaciones transitorias hasta completar la refactorizacion
* parte de la documentacion de `doc/ui/` debera alinearse con este criterio

## Impacto sobre la arquitectura

Esta decision no cambia el reparto base de capas:

* `presentation` sigue manejando interfaz y coordinacion visual
* `application` sigue exponiendo casos de uso y DTOs
* `domain` sigue concentrando reglas puras
* `infrastructure` sigue aislando persistencia y servicios externos

El cambio afecta solo a la organizacion interna de `presentation/`.

## Seguimiento

Fases recomendadas despues de esta ADR:

1. extraer el composition root desde `app/main.py`
2. separar `shell`, `shared` y `features` en el filesystem
3. mover cada feature actual a su carpeta canonica
4. actualizar imports, controladores y documentacion relacionada
