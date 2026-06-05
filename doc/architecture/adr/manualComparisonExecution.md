# Manual Comparison Execution

## Contexto

La comparacion de biblioteca contra playlist puede tardar bastante cuando hay miles de canciones o resultados.

Ejecutarla automaticamente al entrar en la pantalla hacia que la navegacion pareciera rota y metia trabajo costoso sin una accion explicita del usuario.

## Decision

La comparacion pasa a ser manual.

Al entrar en la pantalla:

* si hay cache previa, se muestra
* si la cache esta obsoleta, se sigue mostrando con aviso
* si no hay cache, se muestra un estado informativo

La recomparacion solo se ejecuta cuando el usuario pulsa `Comparar ahora`.

## Consecuencias

* entrar en la pantalla deja de disparar trabajo pesado
* la navegacion es mas estable y predecible
* el usuario controla cuando asumir el coste de recalculo
