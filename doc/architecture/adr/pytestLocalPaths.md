# ADR: Rutas locales de pytest dentro del proyecto

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La suite de tests del proyecto usa archivos con patron `test*.py` en `camelCase`.

Ademas, en algunos entornos Windows `pytest` falla al intentar:

* descubrir tests solo con el patron por defecto
* crear temporales en el directorio global de `Temp`
* reutilizar una cache local previa corrupta

## Decision

La configuracion de `pytest` en `pyproject.toml` queda fijada asi:

* `python_files = ["test*.py"]`
* `--basetemp=.pytestTmp`
* `cache_dir = ".pytestCache"`

Con ello:

* `pytest` descubre la convencion real del proyecto
* los temporales viven dentro del workspace
* la cache local no depende de una estructura previa conflictiva

## Consecuencias

Ventajas:

* ejecucion mas estable en Windows
* menos dependencia del `Temp` global del usuario
* la suite respeta el naming actual del proyecto

Coste:

* aparecen carpetas locales adicionales de test, que deben ignorarse en git
