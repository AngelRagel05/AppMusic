# Playlist Comparison Matching V1

## Contexto

La comparacion entre `youtube_playlist_item` y `local_song` ya dispone de:

* snapshot importado de YouTube
* normalizacion comun para texto musical
* matcher de dominio
* presentacion de resultados en la pantalla `Comparacion`

Faltaba dejar documentado de forma explicita el criterio funcional de matching v1 y sus limites.

## Decision

La comparacion v1 se basa en tres ejes:

* titulo normalizado
* artista normalizado
* duracion como apoyo auxiliar

El matcher calcula un `score` por candidata local y selecciona la mejor.

### Scoring v1

Pesos principales:

* titulo exacto normalizado: peso alto
* artista exacto normalizado: peso alto
* coincidencia parcial por inclusion o solape de tokens: peso medio
* duracion:
  * `+- 3s`: refuerzo alto
  * `+- 5s`: refuerzo medio
  * `+- 8s`: refuerzo bajo

### Estados funcionales

`found`

* el titulo coincide de forma fuerte
* el artista coincide de forma fuerte
* si ambas duraciones existen, la diferencia queda dentro de tolerancia
* el score total supera el umbral de coincidencia clara

`possible_match`

* existe una candidata razonable
* pero no hay evidencia suficiente para darla por encontrada
* puede ocurrir por:
  * titulo parecido pero artista dudoso
  * artista parecido pero titulo no exacto
  * duracion cercana sin coincidencia plena

`missing`

* no existe candidata local que alcance el score minimo esperado
* o la mejor candidata sigue siendo demasiado debil para aceptarse

## Persistencia del resultado

El resultado de comparacion **no se persiste inicialmente**.

Motivos:

* el resultado depende del estado actual de `youtube_playlist_item`
* el resultado depende del estado actual de `local_song`
* guardar ese resultado obligaria a invalidarlo al cambiar playlist o biblioteca
* la app ya puede recalcularlo bajo demanda en segundo plano sin bloquear la UI

La decision detallada de persistencia se mantiene en:

* [playlistComparisonResultPersistence.md](./playlistComparisonResultPersistence.md)

## Limitaciones conocidas

La version v1 tiene limitaciones esperables:

* falsos positivos
  * canciones con titulos muy genericos pueden parecer equivalentes sin serlo
* remixes o versiones live
  * una version `live`, `remix` o `acoustic` puede acabar como `possible_match`
  * en algunos casos incluso podria parecer `found` si el etiquetado local es pobre
* artistas mal etiquetados
  * si el MP3 local o YouTube traen artistas incompletos o inconsistentes, el score baja
* diferencias de duracion
  * intros, silencios, cortes o ediciones pueden mover el resultado entre `found` y `possible_match`

## Consecuencias

* el comportamiento v1 queda documentado y defendible
* la UI puede explicar por que una cancion aparece como encontrada, faltante o dudosa
* futuras mejoras del matching podran compararse contra este baseline funcional
