# SoundShelf

Aplicacion de escritorio local para Windows con tres flujos concretos:

* comparar una playlist de YouTube con una biblioteca de MP3
* editar y verificar metadata embebida en archivos MP3
* descargar audio de YouTube, convertirlo a MP3 e indexarlo

No incluye reproduccion, streaming ni controles de audio.

La interfaz sigue siendo React y la API sigue siendo FastAPI. Electron solo
gestiona la ventana nativa, el arranque y el cierre del servicio local.

## Uso de la aplicacion instalada

El instalador se genera en:

```txt
release/SoundShelf Setup.exe
```

La aplicacion instalada no requiere Python, Node.js, Vite ni FFmpeg del
sistema. Guarda los datos persistentes en:

```txt
%APPDATA%/SoundShelf/
├─ soundshelf.db
├─ logs/
│  ├─ electron.log
│  └─ backend.log
└─ temp/
```

Una actualizacion de los binarios no sobrescribe este directorio. Antes de
iniciar la API, el backend aplica de forma controlada las migraciones Alembic
pendientes.

## Requisitos de desarrollo

* Python 3.12 o superior
* Node.js 22 o superior

## Preparacion

```powershell
Copy-Item .env.example .env
npm run setup
npm run migrate
```

`npm run migrate` permite actualizar manualmente el esquema durante el
desarrollo. El launcher de escritorio ejecuta `alembic upgrade head` antes de
cada arranque. La aplicacion no usa `create_all` ni ejecuta `ALTER TABLE`
fuera de las migraciones.

## Ejecucion en desarrollo

```powershell
npm run app
```

El comando inicia:

* Vite en `http://127.0.0.1:5173`
* Electron con DevTools disponibles
* FastAPI, lanzado por Electron en un puerto local libre

Electron espera a `/api/health` antes de mostrar la ventana. Los logs de Vite,
Electron y FastAPI quedan visibles en la terminal. Para depurar solo la API:

```powershell
npm run app:api
```

## Build de Windows

```powershell
npm run build:desktop
npm run dist
```

`build:desktop` produce `release/win-unpacked`. `dist` produce además el
instalador NSIS `release/SoundShelf Setup.exe`.

El build incluye:

* React compilado
* FastAPI y sus dependencias empaquetados con PyInstaller
* migraciones Alembic y certificados
* yt-dlp y Mutagen
* FFmpeg con su licencia de redistribucion

No se incluye un mecanismo de actualizacion automatica.

## Calidad

```powershell
npm run build
npm run test
npm run lint
npm run verify:backend
```

## Estructura

```txt
app/
├─ api/               # FastAPI, routers y schemas HTTP
├─ application/       # use cases y DTOs
├─ domain/            # entidades, contratos y reglas puras
├─ infrastructure/    # SQLite, filesystem, Mutagen, yt-dlp y tareas
├─ shared/
├─ config/
└─ main.py

desktop/
├─ main.js            # ciclo de vida Electron
├─ backendProcess.js  # puerto, health y proceso FastAPI
├─ preload.js         # frontera minima, sin APIs expuestas
└─ assets/

frontend/
└─ src/
   ├─ app/
   ├─ features/
   ├─ shared/
   └─ styles/
```

La API solo acepta bibliotecas registradas como destinos; nunca expone acceso
general al filesystem.
