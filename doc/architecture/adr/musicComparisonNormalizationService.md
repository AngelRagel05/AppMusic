# Music Comparison Normalization Service

## Contexto

La normalizacion de textos para comparacion musical estaba encapsulada solo en la importacion de YouTube.

Eso no servia para reutilizar las mismas reglas sobre `local_song` al comparar ambos lados.

## Decision

Se extrae un servicio comun en `app/domain/metadata/services/musicComparisonNormalizationService.py`.

Reglas v1:

* minusculas
* `trim`
* colapsar espacios
* quitar ruido: `official`, `video`, `lyrics`, `audio`, `hd`, `4k`, `remastered`
* limpiar brackets y parentesis decorativos
* normalizar separadores como `_`, `:`, `–`, `—`

La estrategia inicial queda asi:

* `youtube_playlist_item` reutiliza el valor normalizado persistido
* `local_song` calculara la normalizacion al vuelo durante el matching

## Consecuencias

* la logica de normalizacion deja de depender solo de YouTube
* el matching futuro puede aplicar las mismas reglas a ambos lados
* no hace falta ampliar todavia la tabla `local_song` con columnas normalizadas
