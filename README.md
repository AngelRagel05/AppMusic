## AppMusic

Base minima para construir una aplicacion de escritorio de musica en Python con `Tkinter` y dejarla preparada para empaquetarse como `.exe` al final con `PyInstaller`.

### Estado actual

- Estructura inicial alineada con `AGENTS.md`
- Arranque de aplicacion con `Tkinter`
- Configuracion central con `.env`
- Logging base con `loguru`
- Base pensada como aplicacion de escritorio, no como libreria
- Sin funcionalidades de dominio implementadas todavia

### Estructura

```txt
app/
tests/
migrations/
```

### Ejecutar

```powershell
.\.venv\Scripts\python.exe -m app.main
```

### Build a EXE

Todavia no estamos generando el `.exe`, pero la base ya esta preparada para hacerlo con `PyInstaller` cuando toque.

Comando previsto:

```powershell
.\.venv\Scripts\pyinstaller.exe AppMusic.spec
```

### Siguiente paso

Definir la primera funcionalidad real y construirla desde la base.
