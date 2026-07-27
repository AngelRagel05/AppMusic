# Contexto del Sistema

## Objetivo

SoundShelf es una aplicacion web local. React ofrece la interfaz y FastAPI
expone un contrato HTTP bajo `/api`; ambos procesos se enlazan exclusivamente
en `127.0.0.1`.

El producto contiene tres herramientas:

1. comparacion de playlist y biblioteca local
2. edicion individual de metadata MP3
3. descarga e indexacion de audio

No existe un contexto de reproduccion, streaming o control de audio.

## Arquitectura

```txt
frontend/React
      |
      | HTTP JSON + polling
      v
app/api/FastAPI
      |
      v
app/application/use_cases
      |
      v
app/domain <--- app/infrastructure
```

```txt
app/
├─ api/
├─ application/
├─ domain/
├─ infrastructure/
│  ├─ downloads/
│  ├─ filesystem/
│  ├─ metadata/
│  ├─ persistence/
│  └─ tasks/
├─ shared/
├─ config/
└─ main.py
```

### API

`app/api/` contiene la aplicacion FastAPI, routers, schemas Pydantic,
dependencias de sesion y el formato estable de errores. Los endpoints no
aceptan rutas de descarga arbitrarias y solo operan sobre bibliotecas
registradas.

### Application

Contiene DTOs y use cases con una accion principal `execute(...)`. Coordina
dominio e interfaces sin depender de FastAPI, SQLAlchemy, Mutagen o yt-dlp.

### Domain

Contiene entidades, contratos de repositorio y reglas puras de biblioteca,
playlists, comparacion, filtros y descargas.

### Infrastructure

Implementa persistencia SQLAlchemy, lectura y escritura Mutagen, filesystem,
yt-dlp, FFmpeg y ejecucion local de tareas.

### Frontend

`frontend/src/` contiene una unica SPA con React Router, TanStack Query y CSS
Modules. Sus rutas publicas son:

* `/comparison`
* `/metadata`
* `/downloads`

`/` redirige al ultimo modulo visitado o a `/comparison`.

## Persistencia

SQLite guarda indice, relaciones, snapshots e intentos de descarga. Los MP3
siguen siendo la fuente real de metadata. Alembic es la unica autoridad del
esquema.

Las claves foraneas de SQLite se habilitan en cada conexion. Las operaciones
complejas controlan `commit` y `rollback` desde el caso de uso o la frontera de
aplicacion.

## Integraciones

* SQLAlchemy y Alembic para persistencia
* Mutagen para leer y escribir tags MP3
* yt-dlp para importar playlists y descargar audio
* FFmpeg, invocado por yt-dlp, para generar MP3

Todas quedan aisladas dentro de `infrastructure`.

## Contratos relacionados

* [youtubePlaylistContext.md](./youtubePlaylistContext.md)
* [localLibraryContext.md](./localLibraryContext.md)
* [comparisonContext.md](./comparisonContext.md)
* [presentationContext.md](./presentationContext.md)
* [runtimeAndQualityContext.md](./runtimeAndQualityContext.md)
