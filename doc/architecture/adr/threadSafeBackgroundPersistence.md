# Thread Safe Background Persistence

## Contexto

La app ejecutaba varias tareas en segundo plano:

* escaneo de biblioteca local
* importacion de items de playlist
* comparacion entre biblioteca y playlist

Esas tareas usaban use cases y repositories construidos con la misma `Session` de SQLAlchemy que tambien quedaba compartida con la UI.

Eso provocaba dos problemas:

* contencion y lentitud impredecible entre hilos
* errores de cierre de sesion al salir de la app mientras un hilo seguia operando

## Decision

Cada tarea en background abre su propio `PersistenceRegistry` dentro del hilo donde se ejecuta.

La operacion:

* crea su propia sesion
* ejecuta sus use cases
* cierra la sesion en el mismo hilo mediante `finally`

La sesion principal queda reservada para el flujo sincronico de la UI.

## Consecuencias

* desaparece el uso compartido inseguro de una misma sesion entre varios hilos
* el cierre de la app deja de competir con transacciones en progreso de otros workers
* se reduce la contencion interna de SQLAlchemy y mejora la respuesta general en operaciones largas
