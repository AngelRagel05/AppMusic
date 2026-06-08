# Front Verification Command

## Contexto

El proyecto es una aplicacion de escritorio con `Tkinter` y `CustomTkinter`.

No existe un paso de build frontend equivalente a una SPA web, pero si hace falta un comando unico para validar rapidamente la capa de presentacion antes de subir cambios o ejecutar CI.

## Decision

Se añade un comando tecnico de verificacion de front basado en:

* `compileall` para validar que el codigo Python del front compila
* `ruff` limitado a errores graves (`E9`, `F63`, `F7`, `F82`)
* `pytest` para controllers, viewmodels y helpers de presentacion

Punto de entrada principal:

* `python scripts/verifyFront.py`

Atajo local en Windows:

* `.\runFrontChecks.ps1`

Integracion en CI:

* GitHub Actions ejecuta el mismo `python scripts/verifyFront.py`
* se evita duplicar reglas entre local y pipeline

## Motivos

* ofrece una experiencia parecida a un `npm run build` para la capa de front
* evita depender de entorno grafico en CI
* evita mezclar convenciones de estilo Python incompatibles con la nomenclatura vigente del proyecto
* concentra en un solo comando los chequeos mas relevantes de presentacion

## Consecuencias

* el equipo tiene una verificacion unica y repetible para front
* los fallos de lint o tests de presentacion se detectan antes de revisar toda la suite
* las pruebas visuales reales siguen siendo una necesidad futura separada
* el pipeline de GitHub Actions reutiliza el mismo comando que el entorno local
