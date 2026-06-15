# Library Comparison Presentation Flow

## Contexto

La pantalla `Comparacion` ya mostraba listas paginadas, pero seguia cargando el matching desde el hilo principal y no reflejaba estados de comparacion reales.

Con bibliotecas y playlists grandes, ese flujo podia bloquear la interfaz.

## Decision

La feature `Comparacion` pasa a usar:

* `LibraryComparisonViewModel`
* `LoadLibraryComparisonWorker`
* `CompareYoutubePlaylistWithLocalLibraryUseCase`

Flujo:

* el controller solicita comparacion al cargar la pantalla
* el viewmodel emite feedback inmediato de inicio
* el worker ejecuta en segundo plano:
  * listado de canciones locales activas
  * comparacion completa contra la playlist activa
* al volver al hilo principal, la UI actualiza:
  * tabla de resultados de comparacion
  * resumen y fecha de ultima comparacion
  * subtitulo con mensaje de estado/resumen

Flujo funcional de revision manual:

* el usuario siempre parte de una fila de resultado asociada a `youtube_playlist_item`
* abre el detalle del resultado
* puede cambiar `match_status`
* puede enlazar o quitar `local_song_id`
* guarda la decision y la tabla se refresca con el snapshot persistido actualizado

Regla de persistencia manual visible en UI:

* la correccion manual queda guardada en el snapshot actual
* `matched_by` distingue si el estado mostrado viene de calculo automatico o de ajuste manual
* si el usuario refresca la comparacion completa, se crea un snapshot nuevo recalculado desde cero

La paginacion existente se conserva y se aplica sobre los resultados comparados.

## Consecuencias

* la comparacion deja de bloquear la interfaz
* la UI muestra estados `Encontrada`, `Falta` y `Posible coincidencia`
* cada item comparado puede enseñar su candidata local sugerida
* cada item comparado puede ser corregido manualmente desde el lado de playlist hacia una cancion local
* el render sigue siendo incremental y paginado
