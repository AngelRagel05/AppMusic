# Contexto de Runtime y Calidad

## Runtime local

`npm run app` ejecuta Vite y Uvicorn en paralelo. El script de API aplica
primero `alembic upgrade head`; el proceso FastAPI valida el esquema y siembra
terminos ignorados, pero no modifica la estructura.

La API escucha en `127.0.0.1`. CORS permite exclusivamente los origenes locales
configurados.

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
pytest, lint frontend, Vitest y el build de produccion.
