# Contexto de Runtime y Calidad

## Runtime local

SoundShelf usa Electron como contenedor y supervisor de procesos:

```txt
Electron
→ React
→ HTTP local
→ FastAPI
→ SQLite / Mutagen / yt-dlp / FFmpeg
```

Electron no contiene reglas de negocio ni accede a SQLite. En desarrollo,
`npm run app` ejecuta Vite y Electron; Electron reserva un puerto local,
aplica las migraciones pendientes y arranca FastAPI. La ventana solo se crea
cuando `/api/health` responde correctamente.

En produccion FastAPI sirve el build estatico de React incluido en la
instalacion. No se ejecutan Vite ni Python del sistema. La API escucha
exclusivamente en `127.0.0.1` y el frontend recibe su URL real en runtime.

El arranque de escritorio aplica `alembic upgrade head` antes de construir la
aplicacion FastAPI. El bootstrap posterior valida el esquema y siembra terminos
ignorados, pero nunca usa `create_all` ni modifica tablas.

## Datos y recursos de escritorio

Electron pasa a FastAPI el directorio `userData` de la aplicacion. En Windows
los datos persistentes quedan bajo `%APPDATA%/SoundShelf`:

```txt
SoundShelf/
├─ soundshelf.db
├─ logs/
│  ├─ electron.log
│  └─ backend.log
└─ temp/
```

La instalacion incluye el backend empaquetado, el build de React y FFmpeg. Las
actualizaciones del programa no sobrescriben la base SQLite ni los logs.

## Ciclo de vida

Solo se permite una instancia de la aplicacion. Al cerrar la ventana, Electron
solicita primero un apagado cooperativo a FastAPI. El `LocalTaskManager` marca
las tareas activas como canceladas y, si el backend o sus procesos hijos no
terminan dentro del plazo, Electron cierra el arbol de procesos de Windows.

## Tareas y concurrencia

`LocalTaskManager` usa un `ThreadPoolExecutor` acotado. Los estados son:

* `queued`
* `running`
* `cancelling`
* `completed`
* `failed`
* `cancelled`

Escaneo, importacion, comparacion y descarga se ejecutan fuera del ciclo HTTP.
Cada operacion abre su propia sesion SQLAlchemy y la cierra al terminar. La
cancelacion es cooperativa: `cancelling` solo pasa a `cancelled` cuando la
operacion confirma que se ha detenido.

## Integridad de metadata

La edicion sigue siempre este orden:

```txt
validar archivo dentro de biblioteca registrada
→ escribir tags con Mutagen
→ releer el MP3
→ actualizar SQLite con los valores confirmados
```

## Testing

```txt
tests/
├─ unit/
└─ integration/

frontend/src/**/*.test.js(x)
```

La verificacion completa usa:

```powershell
npm run lint
npm run test
npm run build
```

Backend cubre dominio, use cases, repositorios, migracion/arranque, tareas y
API. Frontend cubre navegacion y cliente HTTP con Vitest y Testing Library.

## CI

CI instala Python y Node, ejecuta Alembic sobre una base temporal, Ruff,
pytest, las pruebas Node del launcher, lint frontend, Vitest y el build de
produccion. El instalador NSIS se construye en un job Windows separado.
