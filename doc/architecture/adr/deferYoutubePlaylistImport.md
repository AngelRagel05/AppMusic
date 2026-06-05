# Defer Youtube Playlist Import

## Contexto

En el arranque de la app, la carga inicial de la seccion de playlists lanzaba automaticamente una importacion completa de la playlist activa.

Eso introducia coste de red, parsing y persistencia aunque el usuario no hubiera abierto la seccion ni solicitado sincronizacion.

## Decision

La importacion de playlists deja de ejecutarse automaticamente en `load()`.

La sincronizacion queda como accion explicita del usuario.

## Consecuencias

* el arranque de la app es mas rapido
* se evita trabajo remoto y persistencia innecesaria en segundo plano
* la actualizacion de la playlist se hace cuando el usuario realmente la solicita
