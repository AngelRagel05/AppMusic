# Politica de cache bytecode de Python

## Decision

El proyecto define `PYTHONDONTWRITEBYTECODE=1` en `.env` y debe arrancarse mediante `runApp.ps1`.

## Motivo

Python genera directorios `__pycache__` cuando importa modulos para guardar bytecode compilado.
En este proyecto esos artefactos molestan en el arbol de `app/`, `tests/` y `migrations/`, y no aportan valor durante el desarrollo habitual.

## Implementacion

`runApp.ps1` lee `PYTHONDONTWRITEBYTECODE` desde `.env` antes de invocar Python.
Esto es necesario porque el interprete decide si escribe bytecode antes de que `app/config/settings.py` ejecute `load_dotenv()`.

## Uso

Desde la raiz del proyecto:

```powershell
.\runApp.ps1
```

Si se arranca la app por otra via, por ejemplo con `python -m app.main`, la variable debe estar exportada previamente en la sesion para evitar nuevos `__pycache__`.
