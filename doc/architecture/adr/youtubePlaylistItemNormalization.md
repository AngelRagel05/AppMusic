# ADR: Normalizacion minima de items de playlist de YouTube

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La tabla `youtube_playlist_item` ya guarda `raw_title`, `raw_channel_name`, `normalized_title` y `normalized_artist`.

Antes de implementar la importacion real y el matching contra `local_song`, hace falta fijar una normalizacion minima reutilizable para que el snapshot persistido no dependa del formato textual bruto de YouTube.

## Decision

Se introduce un servicio puro de dominio para normalizar metadata basica de items de YouTube.

Reglas minimas v1:

* convertir a minusculas
* aplicar `trim`
* colapsar espacios duplicados
* quitar ruido decorativo tipico:
  * `official video`
  * `official audio`
  * `lyrics`
  * `hd`
  * `4k`
  * `remastered`
* eliminar bloques entre parentesis o corchetes cuando solo contienen ese ruido
* si el titulo sigue el patron `artista - cancion`, usar la parte izquierda como `normalized_artist` y la derecha como `normalized_title`
* si no existe ese patron, usar `raw_channel_name` normalizado como fallback de artista

## Consecuencias

Ventajas:

* la importacion futura puede persistir ya campos comparables sin depender de la UI
* la comparacion posterior contra `local_song` parte de una base mas estable
* la logica queda encapsulada en dominio y se puede testear sin infraestructura externa

Costes:

* la inferencia de artista en v1 sigue siendo heuristica y puede fallar en formatos complejos
* algunos casos de ruido no quedaran cubiertos hasta fases posteriores

## Fuera de alcance

En esta fase no se implementa:

* matching fuzzy contra `local_song`
* soporte completo para `feat.`, `ft.` o colaboradores multiples
* normalizacion avanzada por idioma o transliteracion
