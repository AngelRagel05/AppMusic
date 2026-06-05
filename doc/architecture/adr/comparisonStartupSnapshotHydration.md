# Comparison Startup Snapshot Hydration

## Contexto

La pantalla `Comparacion` ya persistia el resultado en:

* `playlist_comparison`
* `playlist_comparison_result`

Sin embargo, al reiniciar la app, la pestaña seguia vacia porque solo reutilizaba caché en memoria del proceso actual.

## Decision

Al abrir `Comparacion`, si no existe caché en memoria, la app intenta cargar el ultimo snapshot persistido para:

* la playlist activa
* la biblioteca local activa

Si encuentra ese snapshot:

* hidrata la caché del `LibraryComparisonViewModel`
* reconstruye `PlaylistComparisonResultDto`
* muestra el resultado sin obligar al usuario a recomparar

## Motivos

* evita que una comparacion ya guardada desaparezca tras reiniciar la app
* reutiliza persistencia ya existente en vez de recalcular innecesariamente
* mantiene el flujo manual de `Comparar ahora` como accion explicita para refrescar

## Consecuencias

* la primera apertura de `Comparacion` puede leer datos desde BBDD
* el resultado inicial mostrado pasa a ser el ultimo snapshot persistido del ambito activo
* si no existe snapshot persistido, la pantalla mantiene el mensaje manual actual
