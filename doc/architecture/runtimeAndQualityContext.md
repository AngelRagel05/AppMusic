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

## Canales de distribucion

El mismo codigo fuente genera dos identidades de Windows. Produccion usa
`com.angelragel.soundshelf`, el nombre `SoundShelf` y solo se empaqueta desde
`main`. Beta usa `com.angelragel.soundshelf.beta`, el nombre `SoundShelf Beta`
y solo se empaqueta desde ramas distintas de `main`.

La configuracion comun de electron-builder se crea una sola vez. El script de
distribucion detecta la rama con `git branch --show-current`, valida el canal y
despues selecciona las diferencias de identidad, ejecutable, instalador, icono
y accesos directos. El canal se embebe como metadata del paquete para que no
dependa de variables externas durante la ejecucion.

## Datos y recursos de escritorio

Electron resuelve la identidad antes de pedir el bloqueo de instancia y pasa a
FastAPI el directorio `userData` correspondiente. En Windows, produccion usa
`%APPDATA%/SoundShelf`:

```txt
SoundShelf/
├─ soundshelf.db
├─ logs/
│  ├─ electron.log
│  └─ backend.log
└─ temp/
```

Beta conserva la misma estructura en `%APPDATA%/SoundShelf Beta`. Las
aplicaciones empaquetadas no admiten sobreescribir externamente esta ruta, de
modo que la SQLite, configuracion, logs, temporales y estado de ventana siempre
quedan separados.

Cada instalacion incluye el backend empaquetado, el build de React y FFmpeg.
Las actualizaciones del programa no sobrescriben la base SQLite ni los logs.

## Ciclo de vida

Solo se permite una instancia por canal. Las rutas `userData`, los ejecutables
y los AppUserModelID distintos permiten ejecutar una instancia estable y otra
Beta al mismo tiempo. Al cerrar una ventana, su Electron solicita primero un
apagado cooperativo a su FastAPI. El `LocalTaskManager` marca las tareas
activas como canceladas y, si el backend o sus procesos hijos no terminan
dentro del plazo, Electron cierra su arbol de procesos de Windows.

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
