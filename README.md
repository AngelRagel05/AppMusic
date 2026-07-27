# SoundShelf

Aplicacion web local para tres flujos concretos:

* comparar una playlist de YouTube con una biblioteca de MP3
* editar y verificar metadata embebida en archivos MP3
* descargar audio de YouTube, convertirlo a MP3 e indexarlo

No incluye reproduccion, streaming ni controles de audio.

## Requisitos

* Python 3.12 o superior
* Node.js 22 o superior
* FFmpeg disponible en `PATH` o configurado mediante `FFMPEG_PATH`

## Preparacion

```powershell
Copy-Item .env.example .env
npm run setup
npm run migrate
```

`npm run migrate` es la unica via autorizada para crear o actualizar el
esquema. La aplicacion no ejecuta `create_all` ni `ALTER TABLE` al arrancar.

## Ejecucion

```powershell
npm run app
```

El comando inicia simultaneamente:

* FastAPI en `http://127.0.0.1:8000`
* Vite en `http://127.0.0.1:5173`

La documentacion OpenAPI queda en `http://127.0.0.1:8000/api/docs`.

## Calidad

```powershell
npm run build
npm run test
npm run lint
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

frontend/
└─ src/
   ├─ app/
   ├─ features/
   ├─ shared/
   └─ styles/
```

La base SQLite y las rutas configuradas se resuelven desde la raiz del
proyecto. La API solo acepta bibliotecas registradas como destinos; nunca
expone acceso general al filesystem.
