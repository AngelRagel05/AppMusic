# ADR: Mapa modular del dominio

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La arquitectura objetivo ya fija que el dominio debe evolucionar desde carpetas globales:

* `domain/entities/`
* `domain/repositories/`
* `domain/services/`

hacia una organizacion modular por responsabilidad:

```txt
domain/<module>/
```

El problema actual es que el dominio todavia esta agrupado por tipo tecnico y no por modulo funcional.

## Decision

Se define el mapa modular del dominio del proyecto usando dos categorias:

* modulos reales actuales
* modulos previstos pero todavia no implementados

La reorganizacion futura del codigo debe seguir este mapa y evitar volver a carpetas genericas grandes.

## Modulos reales actuales

### `library`

Responsabilidad:

* gestionar bibliotecas locales
* definir carpeta principal
* activar biblioteca
* actualizar biblioteca
* eliminar biblioteca

Contenido de dominio asignado:

* entidad: `LocalFolder`
* contrato de repositorio: `LocalFolderRepository`

Use cases relacionados en `application/`:

* `DefineMainLocalFolderUseCase`
* `ActivateLocalFolderUseCase`
* `UpdateLocalFolderUseCase`
* `DeleteLocalFolderUseCase`
* `ListLocalFoldersUseCase`
* `GetActiveLocalFolderUseCase`

Estructura objetivo:

```txt
app/domain/library/
├── entities/
│   └── localFolder.py
├── repositories/
│   └── localFolderRepository.py
├── services/
├── actions/
└── interfaces/
```

### `playlists`

Responsabilidad:

* gestionar playlists de YouTube de referencia
* definir playlist principal
* activar playlist
* actualizar playlist
* eliminar playlist

Contenido de dominio asignado:

* entidad: `YoutubePlaylist`
* contrato de repositorio: `YoutubePlaylistRepository`

Use cases relacionados en `application/`:

* `DefineMainYoutubePlaylistUseCase`
* `ActivateYoutubePlaylistUseCase`
* `UpdateYoutubePlaylistUseCase`
* `DeleteYoutubePlaylistUseCase`
* `ListYoutubePlaylistsUseCase`
* `GetActiveYoutubePlaylistUseCase`

Estructura objetivo:

```txt
app/domain/playlists/
├── entities/
│   └── youtubePlaylist.py
├── repositories/
│   └── youtubePlaylistRepository.py
├── services/
├── actions/
└── interfaces/
```

### `filters`

Responsabilidad:

* gestionar terminos ignorados
* crear filtros de limpieza
* actualizar filtros
* eliminar filtros
* listar filtros

Contenido de dominio asignado:

* entidad: `IgnoredTerm`
* contrato de repositorio: `IgnoredTermRepository`

Use cases relacionados en `application/`:

* `CreateIgnoredTermUseCase`
* `UpdateIgnoredTermUseCase`
* `DeleteIgnoredTermUseCase`
* `ListIgnoredTermsUseCase`

Estructura objetivo:

```txt
app/domain/filters/
├── entities/
│   └── ignoredTerm.py
├── repositories/
│   └── ignoredTermRepository.py
├── services/
├── actions/
└── interfaces/
```

## Modulos previstos

Estos modulos encajan con el objetivo funcional del proyecto y con las integraciones ya presentes en `infrastructure/`, pero todavia no tienen suficiente dominio implementado como para crear estructura definitiva en codigo.

### `metadata`

Responsabilidad prevista:

* lectura y normalizacion de metadatos musicales
* reglas de comparacion de titulo, artista, album y limpieza
* coordinacion conceptual con Mutagen

Se usara cuando aparezcan:

* value objects de metadata
* reglas puras de normalizacion
* acciones de dominio sobre etiquetado o comparacion

### `downloads`

Responsabilidad prevista:

* decisiones de negocio sobre descargas
* estados de descarga
* reglas para preparar audio descargado o procesado

Se usara cuando aparezcan:

* entidad de descarga
* politicas de reintento, estado o prioridad
* coordinacion conceptual sobre yt-dlp y FFmpeg

### `playback`

Responsabilidad prevista:

* reproduccion local
* estado de reproduccion
* acciones de play, pause, stop, seek si terminan teniendo peso de dominio

Solo debe crearse si la reproduccion deja de ser un detalle puramente tecnico de infraestructura.

### `sync`

Responsabilidad prevista:

* comparacion entre biblioteca local y playlist remota
* reglas de sincronizacion
* resultados de diferencias y decisiones de actualizacion

Este modulo es especialmente importante si el proyecto evoluciona hacia reconciliacion de canciones, metadatos y estados.

## Reglas de asignacion

### Entidades

Una entidad debe vivir en el modulo donde su responsabilidad principal tenga sentido funcional.

Ejemplos:

* `LocalFolder` -> `library`
* `YoutubePlaylist` -> `playlists`
* `IgnoredTerm` -> `filters`

### Repositorios

Un contrato de repositorio debe vivir en el mismo modulo que la entidad o agregado que persiste.

No deben mantenerse repositorios globales en `domain/repositories/` a largo plazo si el dominio ya esta modularizado.

### Servicios de dominio

`services/` solo debe usarse cuando exista una regla de negocio real que no pertenezca claramente a una sola entidad.

No debe usarse como carpeta comodin para contratos de persistencia.

### Actions

`actions/` se reserva para operaciones de dominio concretas cuando ayuden a expresar mejor una regla o flujo de negocio reutilizable.

No es obligatorio crearla por modulo desde el primer dia si no aporta claridad.

### Interfaces

`interfaces/` solo debe existir cuando una abstraccion externa aporte valor semantico claro al dominio.

No debe llenarse por defecto.

## Estructura objetivo consolidada

```txt
app/domain/
├── library/
│   ├── entities/
│   ├── repositories/
│   ├── services/
│   ├── actions/
│   └── interfaces/
├── playlists/
│   ├── entities/
│   ├── repositories/
│   ├── services/
│   ├── actions/
│   └── interfaces/
├── filters/
│   ├── entities/
│   ├── repositories/
│   ├── services/
│   ├── actions/
│   └── interfaces/
├── metadata/
├── downloads/
├── playback/
└── sync/
```

## Alcance inmediato

A corto plazo, la siguiente fase de refactor debe centrarse en:

1. mover `LocalFolder` y `LocalFolderRepository` a `domain/library/`
2. mover `YoutubePlaylist` y `YoutubePlaylistRepository` a `domain/playlists/`
3. mover `IgnoredTerm` e `IgnoredTermRepository` a `domain/filters/`

Los modulos `metadata`, `downloads`, `playback` y `sync` quedan definidos como direccion arquitectonica, pero no deben llenarse artificialmente hasta que exista dominio real para ellos.

## Consecuencias

Ventajas:

* el dominio deja de crecer por carpetas tecnicas globales
* el lenguaje del proyecto se alinea mejor con DDD light
* se facilita relacionar entidades, reglas, contratos y casos de uso por modulo funcional

Costes:

* mover codigo requerira actualizar imports en `application`, `infrastructure`, `presentation` y tests
* durante la transicion coexistiran estructura actual y estructura objetivo hasta completar la migracion
