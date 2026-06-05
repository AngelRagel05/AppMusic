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
  * columna izquierda con canciones locales
  * columna derecha con resultados de matching
  * subtitulo con mensaje de estado/resumen

La paginacion existente se conserva y se aplica sobre los resultados comparados.

## Consecuencias

* la comparacion deja de bloquear la interfaz
* la UI muestra estados `Encontrada`, `Falta` y `Posible coincidencia`
* cada item comparado puede enseñar su candidata local sugerida
* el render sigue siendo incremental y paginado
