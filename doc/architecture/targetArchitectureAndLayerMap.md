# ADR: Arquitectura objetivo y mapa de capas

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

El proyecto necesita una referencia arquitectonica global que unifique:

* separacion de responsabilidades
* reglas de dependencia entre capas
* criterio de modularidad
* adaptacion de la propuesta ideal del usuario al repositorio real

La propuesta objetivo del usuario parte de una estructura tipo `src/app/...` y `docs/...`, pero este proyecto ya trabaja con:

* codigo dentro de `app/`
* documentacion tecnica dentro de `doc/`

Segun `AGENTS.md`, esa convencion debe respetarse.

## Decision

La arquitectura objetivo del proyecto se implementa sobre la estructura real del repositorio:

* codigo en `app/`
* documentacion tecnica en `doc/`

No se introduce una raiz `src/` ni se sustituye `doc/` por `docs/`.

La referencia objetivo queda asi:

```txt
app/
├── bootstrap/
├── presentation/
├── application/
├── domain/
├── infrastructure/
├── shared/
├── workers/
└── config/

doc/
├── architecture/
├── ui/
└── bbdd/
```

## Objetivo de cada capa

### `presentation/`

Responsabilidad:

* mostrar datos
* recoger interacciones del usuario
* coordinar navegacion y estado visual

No debe:

* ejecutar logica de negocio pesada
* acceder directamente a base de datos
* usar directamente SQLAlchemy, yt-dlp, FFmpeg, Mutagen o pygame

Flujo esperado:

* `UI -> ViewModel/Controller -> UseCase`

### `application/`

Responsabilidad:

* orquestar casos de uso
* transformar datos de entrada y salida
* coordinar servicios de dominio y contratos

No debe:

* depender de widgets o detalles de UI
* contener adaptadores concretos de infraestructura

### `domain/`

Responsabilidad:

* entidades
* reglas de negocio
* servicios de dominio
* acciones de dominio si aportan claridad
* contratos de repositorio y abstracciones de dominio

No debe:

* depender de SQLAlchemy
* depender de Tkinter o CustomTkinter
* conocer APIs externas concretas

### `infrastructure/`

Responsabilidad:

* persistencia
* adaptadores a SQLite, SQLAlchemy, Alembic
* integraciones con Mutagen, yt-dlp, FFmpeg, pygame y otras herramientas externas
* configuracion tecnica
* logging tecnico

No debe:

* decidir reglas de negocio del dominio
* contener coordinacion de UI

### `shared/`

Responsabilidad:

* utilidades transversales
* excepciones compartidas
* constantes comunes

No debe:

* convertirse en una capa comodin para mezclar negocio, UI e infraestructura

### `bootstrap/`

Responsabilidad:

* composition root
* construccion y cableado de dependencias
* arranque de la aplicacion

### `workers/`

Responsabilidad:

* tareas que pueden bloquear la UI
* ejecucion en segundo plano
* devolucion de resultados a `presentation`

## Mapa de dependencias permitido

Regla general:

```txt
presentation -> application -> domain
infrastructure -> domain
bootstrap -> presentation + application + infrastructure + domain
workers -> application + infrastructure + domain
```

Detalle practico:

* `presentation` puede depender de `application`
* `presentation` puede depender de `shared`
* `application` puede depender de `domain`
* `application` no debe depender de `presentation`
* `domain` no debe depender de `application`, `presentation` ni `infrastructure`
* `infrastructure` puede implementar contratos definidos en `domain`
* `bootstrap` puede conocer todas las capas para componer la app
* `workers` pueden usar `application` y `infrastructure`, pero no actualizar widgets directamente

## Dependencias prohibidas

Quedan explicitamente prohibidas estas relaciones:

* `presentation -> infrastructure` directa para persistencia o integraciones externas
* `presentation -> domain` para saltarse casos de uso
* `domain -> infrastructure`
* `domain -> presentation`
* `application -> presentation`
* widgets o ventanas hablando directamente con SQLAlchemy, pygame, yt-dlp, FFmpeg o Mutagen

## Modularidad esperada

La arquitectura debe tender a modulos funcionales con responsabilidad clara.

Objetivo recomendado:

```txt
domain/
└── <module>/
    ├── entities/
    ├── services/
    ├── actions/
    ├── repositories/
    └── interfaces/
```

Y en presentacion:

```txt
presentation/
├── shell/
├── shared/
└── features/
```

No se obliga a crear carpetas vacias, pero si a respetar el criterio de responsabilidad.

## Criterios de implementacion

* aplicar SOLID con pragmatismo
* preferir clases y funciones pequenas
* evitar god objects
* encapsular cada integracion externa en `infrastructure`
* mantener los viewmodels como coordinadores ligeros de UI
* documentar decisiones tecnicas importantes en `doc/architecture/`

## Consecuencias

Ventajas:

* criterio unico para futuras refactorizaciones
* menos ambiguedad sobre donde debe vivir cada pieza
* lenguaje mas limpio entre negocio, casos de uso, UI e infraestructura

Costes:

* la migracion completa requiere varias fases
* algunas carpetas actuales conviviran temporalmente con la estructura objetivo hasta terminar la transicion
