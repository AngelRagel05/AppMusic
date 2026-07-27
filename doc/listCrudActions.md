# Acciones CRUD en listas principales

## Objetivo

Unificar la operativa de `local_folder` y `youtube_playlist` alrededor de listas con acciones
claras sobre la seleccion actual.

## Decision

Las secciones de bibliotecas locales y playlists de YouTube usan una tabla donde cada fila
tiene una ultima columna `Acciones` con un boton-menu.

Ese menu por fila ofrece:

* `Editar`
* `Eliminar`

La creacion y actualizacion se hacen en el formulario superior. Cuando el usuario pulsa
`Editar`, el formulario entra en modo actualizacion sobre el elemento seleccionado.
La activacion deja de vivir en un boton lateral y pasa a ejecutarse con doble clic sobre la fila.

## Motivo

* evita ocupar un panel lateral permanente para acciones de fila
* mantiene una interfaz local clara y cercana a un patron de lista contextual
* permite ocultar informacion secundaria como la URL completa en la lista de playlists

## Reglas aplicadas

* `youtube_playlist` ya no muestra la URL completa en la tabla
* `local_folder` mantiene la ruta visible porque es el dato operativo principal
* `title` sigue siendo el nombre visible de la playlist
* `external_playlist_id` sigue siendo el id externo de YouTube
