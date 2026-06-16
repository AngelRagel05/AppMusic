# ADR: normalizacion, evidencia y clasificacion del matching de comparacion

## Estado

Aceptada

## Contexto

La comparacion entre playlist y biblioteca local estaba tomando decisiones de negocio demasiado apoyadas en un score total opaco.

Eso generaba varios problemas:

* coincidencias claras que quedaban en `possible_match`
* falsos `found` empujados por score global sin suficiente contexto
* dependencia excesiva del snapshot normalizado persistido
* mensajes de razon demasiado genericos para entender por que una cancion quedaba en `missing` o `possible_match`
* heuristicas de YouTube fragiles ante formatos reales como:
  * `NN. Artista - Cancion`
  * `02 - TITULO - ARTISTA`
  * `ARTISTA | TITULO`
  * titulos con `ft`, `feat`, `visualizer`, `lyrics`, `topic` y ruido editorial

## Decision

Se sustituye el criterio legacy por un pipeline declarativo de comparacion:

1. rehacer normalizacion
2. rehacer modelo de evidencia
3. rehacer clasificacion
4. resolver ambigüedad entre top candidatos
5. ajustar reasons y persistencia
6. añadir tests reales
7. refresh y medir conteos

## Que logica legacy se elimina

Se elimina expresamente:

* clasificacion puramente por umbral total en `classifyMatchStatus`
* rescates legacy por score global sin contexto
* reglas de `possible_match` basadas solo en alcanzar un score minimo
* dependencia conceptual del normalizado persistido como verdad unica
* mensajes de razon demasiado genericos
* inferencia de ambigüedad basada en conteos globales de candidatas sin comparar de verdad el top ranking

## Como se sustituye

Se sustituye por:

* reglas explicitas por evidencia
* parser de YouTube mas robusto
* resolucion top-2 candidate
* `possible_match` solo por ambigüedad real o por caso exacto sin artista y duracion superior a `1s`
* score como apoyo y ordenacion, no como juez final

## Normalizacion nueva

La normalizacion deja de mezclar ruido, separadores y decision de negocio en una sola pasada.

Ahora:

* existe una politica unica de terminos ignorados de comparacion
* se separan:
  * titulo principal
  * artista principal
  * colaboradores
  * decoradores ignorables
* se recalcula siempre desde `raw_title` y `raw_channel_name`
* `album` queda preparado como señal opcional, pero no bloquea el matching cuando YouTube no lo aporta

### Terminos ignorados base

Ejemplos base:

* `ft`
* `feat`
* `featuring`
* `prod`
* `official`
* `audio`
* `visualizer`
* `topic`
* `lyrics`
* `letra`

No se ignoran por defecto:

* `remix`
* `live`
* `version`

## Parser de YouTube

El parser de YouTube ya no depende de una sola forma de titulo.

Soporta explicitamente varios formatos reales:

* `Artista - Titulo`
* `NN. Artista - Titulo`
* `02 - TITULO - ARTISTA`
* `ARTISTA | TITULO`
* variantes con separadores `-`, `|`, `///`, `/`, `:`, `·`, `~`
* variantes donde el canal precede al titulo con formato `CANAL  #TITULO`
* titulos con ruido editorial, brackets y sufijos decorativos

La separacion `artista/titulo` se hace antes de perder los separadores durante la limpieza.

Ademas:

* no se promociona `contains` como evidencia casi suficiente para decidir artista
* el canal se usa como pista auxiliar, no como verdad absoluta

## Modelo de evidencia

La decision deja de girar alrededor de un numero total y pasa a usar evidencia explicita por candidato:

* coincidencia de titulo:
  * `exact`
  * `near_exact`
  * `contains`
  * `weak`
  * `none`
* coincidencia de artista:
  * `strong`
  * `medium`
  * `weak`
  * `none`
* coincidencia de duracion:
  * `<=1s`
  * `<=3s`
  * `>3s`
  * `unknown`

El score sigue existiendo, pero solo para:

* ordenar candidatos
* detectar empates cercanos
* explicar por que algo queda en `possible_match`

## Significado actual de los estados

### FOUND

`FOUND` significa que hay evidencia suficiente de que la cancion local y la cancion de la playlist representan la misma pista.

Reglas activas:

* `found` si titulo `exact` o `near_exact` y artista `strong`
* `found` si titulo `exact`, artista `strong` y duracion razonable

### POSSIBLE_MATCH

`POSSIBLE_MATCH` queda reservado a casos donde todavia hay una duda real.

Reglas activas:

* `possible_match` si titulo `exact`, artista `none` y duracion `>1s`
* `possible_match` si, tras comparar titulo, artista y duracion, siguen existiendo dos candidatas plausibles y no se puede romper el empate

Regla importante:

* `possible_match` ya no significa "ha llegado a un score intermedio"
* `possible_match` queda reservado a ambigüedad real o a ausencia real de artista con titulo exacto y duracion no fuerte

### MISSING

`MISSING` significa que no hay una candidata local suficientemente competitiva bajo las reglas de evidencia actuales.

Ejemplos tipicos:

* titulo solo `contains`
* artista inconsistente
* duracion fuera de tolerancia fuerte sin apoyo suficiente
* no existe ninguna candidata real en local

## Resolucion de ambigüedad

La ambigüedad ya no se deduce por un `best_sort_key` aislado ni por un conteo global de candidatos.

Ahora el flujo es:

1. calcular ranking de candidatos
2. comparar el primero con el segundo
3. validar si el segundo sigue siendo plausible
4. intentar romper el empate por:
   * titulo
   * artista
   * duracion
5. solo si no se puede romper de forma segura, clasificar como `possible_match`

Esto reduce `possible_match` espurios y deja esa etiqueta reservada para ambigüedad real.

## Reasons y persistencia

Los motivos de negocio dejan de ser mensajes genericos basados solo en `status + score`.

Ahora:

* el matcher genera motivos concretos y funcionales
* el snapshot persistido reutiliza ese motivo compacto en `matched_by`
* la rehidratacion no inventa un texto peor que el original
* la UI muestra el motivo funcional en lugar de resumirlo con frases vagas

Ejemplos de motivos actuales:

* `Titulo exacto con artista fuerte y duracion razonable.`
* `Titulo casi exacto con artista fuerte.`
* `Titulo exacto pero artista inconsistente.`
* `Ambiguedad entre dos candidatas plausibles.`
* `Duracion fuera de tolerancia fuerte.`
* `Titulo competitivo pero artista inconsistente.`

## Consecuencias

### Positivas

* menos falsos `possible_match`
* menos falsos `found` empujados por score global
* parser de YouTube mas robusto para formatos reales
* mejor explicacion funcional en snapshots y UI
* menor dependencia de normalizados persistidos como verdad unica
* mejor capacidad de añadir regresiones reales en tests

### Riesgos

* la clasificacion `found` es mas estricta y puede mover casos antiguos a `missing`
* algunos canales editoriales de YouTube pueden seguir requiriendo ajustes finos
* endurecer `contains` obliga a que la normalizacion y el parser sigan mejorando con casos reales

## Implementacion

Los cambios principales viven en:

* `app/domain/metadata/services/musicComparisonNormalizationService.py`
* `app/domain/playlists/services/youtubePlaylistItemNormalizationService.py`
* `app/domain/playlists/services/playlistItemMatchingRules.py`
* `app/domain/playlists/services/persistedPlaylistItemMatcherService.py`
* `app/application/use_cases/playlists/compareYoutubePlaylistWithLocalLibraryUseCase.py`
* `app/application/use_cases/playlists/loadPersistedPlaylistComparisonUseCase.py`
* `app/presentation/features/comparison/comparisonReasonSummary.py`

## Validacion recomendada

Despues de aplicar estos cambios, la validacion recomendada es:

* ejecutar tests unitarios de normalizacion, matching y use cases
* refrescar comparacion sobre datos reales
* medir conteos de `found`, `possible_match` y `missing`
* revisar especificamente los casos reales convertidos a no regresion:
* `Folele`
* `Practice`
* `G Wagon`
* `Eshate Pa Ca`
* `Donde Duele Mas`
* `NADAL 015  #MEMORIES I`
* `Platos Rotos`
* `NATOS | SELECTA Motorseries #01`
* `02 - SINCERAMENTE - CHEB RUBEN`
