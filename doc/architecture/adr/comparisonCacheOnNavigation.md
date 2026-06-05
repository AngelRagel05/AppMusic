# Comparison Cache On Navigation

## Contexto

La seccion de comparacion ejecutaba una nueva comparacion completa cada vez que el usuario entraba en la vista, aunque la biblioteca local activa y la playlist activa no hubieran cambiado.

Ese comportamiento hacia lenta la navegacion porque el controlador relanzaba el worker y el render de resultados en cada apertura de la seccion.

## Decision

Se reutiliza el ultimo resultado de comparacion mientras siga siendo valido.

La comparacion se marca como obsoleta solo cuando cambia alguna de sus fuentes:

* biblioteca local activa
* resultado de escaneo de biblioteca
* playlist activa
* resultado de importacion de playlist

Cuando la vista de comparacion se abre:

* si existe cache valida, se reutiliza sin recalcular
* si la cache esta obsoleta o no existe, se lanza una nueva comparacion

## Consecuencias

* la navegacion hacia Comparacion vuelve a ser inmediata en reentradas normales
* se mantiene consistencia funcional porque la cache se invalida cuando cambian los datos base
* el coste de comparacion sigue existiendo, pero solo cuando realmente hace falta recalcular
