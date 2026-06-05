# Playlist Item Matching Ruleset

## Contexto

El matching entre `youtube_playlist_item` y `local_song` estaba concentrado en un unico servicio con:

* pesos hardcodeados
* helpers privados
* clasificacion y razon mezcladas con el recorrido de candidatas

Eso dificultaba probar reglas concretas de forma aislada y extender el algoritmo sin tocar el servicio principal completo.

## Decision

Se extraen las reglas de matching a un `ruleset` explicito con funciones puras reutilizables:

* pesos de texto
* umbrales de duracion
* umbrales de clasificacion
* funciones de scoring
* funcion de clasificacion
* funcion de construccion del motivo

El servicio `matchYoutubePlaylistItemToLocalSongs(...)` mantiene su API publica y pasa a orquestar:

* iteracion de candidatas
* seleccion de la mejor
* uso del `ruleset` por defecto o uno inyectado

## Motivos

* probar cada regla sin depender del flujo completo del matcher
* facilitar futuras extensiones por configuracion o nuevas estrategias
* mantener estable el punto de entrada usado por aplicacion

## Consecuencias

* las reglas de matching quedan desacopladas del recorrido de candidatas
* el dominio expone un contrato mas claro para evolucionar pesos y umbrales
* los tests pueden cubrir scoring, clasificacion y razones de forma separada
