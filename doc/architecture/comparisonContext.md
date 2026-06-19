# Contexto de Comparacion

## Objetivo

Unificar en un solo documento el flujo funcional, tecnico y de persistencia de la comparacion entre playlist de YouTube y biblioteca local.

## Flujo vigente

El flujo activo y canónico es:

1. normalizacion simetrica entre playlist y local
2. filtro duro por titulo comparable
3. filtro duro por artista comparable dentro del subconjunto del titulo
4. exclusion de `local_song` reservadas por `FOUND`
5. score final solo dentro del subconjunto ya validado
6. clasificacion en `FOUND`, `POSSIBLE_MATCH` o `MISSING`
7. persistencia de snapshot de comparacion

Queda retirado del flujo activo cualquier esquema por lotes o amplitud progresiva.

Ya no forman parte del comportamiento vigente:

* seleccion por etapas `EXACT`, `VERY_SIMILAR`, `BROAD`
* competicion de candidatas solo por similitud de titulo
* entrada de candidatas con artista no validado al score final
* posibilidad de llegar a `POSSIBLE_MATCH` por titulo y duracion sin validar antes el artista

## Modelo comparable rediseñado

La Fase 2 elimina la asimetria funcional actual entre:

* playlist con comparables ya normalizados
* biblioteca local aun expuesta al matcher mediante `title` y `artist`

El matcher debe trabajar sobre un contrato comparable homogéneo.

### Contrato objetivo

`ComparableYoutubePlaylistItem` debe exponer:

* `id`
* `comparable_title`
* `comparable_artist_full`
* `comparable_artist_primary`
* `comparable_artist_collaborators` opcional
* `duration_seconds`

`ComparableLocalSong` debe exponer:

* `id`
* `comparable_title`
* `comparable_artist_full`
* `comparable_artist_primary`
* `comparable_artist_collaborators` opcional
* `duration_seconds`
* `is_available`
* `is_reserved` cuando la orquestacion lo necesite

La comparacion deja de usar `title` y `artist` como superficie funcional del contrato comparable.

Regla semantica del contrato:

* `primary` representa el artista base de decision
* `full` representa la cadena comparable completa
* `collaborators` sirve como apoyo y nunca como llave principal de `FOUND`

### Decision de persistencia

Se decide persistir campos comparables tambien en `local_song`.

Motivos:

* evita recalcular la normalizacion completa en cada matching
* alinea playlist y biblioteca local bajo el mismo contrato de datos comparables
* permite que fingerprints, snapshots e incrementalidad describan exactamente los valores comparables usados por el matcher
* deja la preparacion de comparables en scan/import y no dentro del matcher

La fase de preparacion sigue existiendo, pero ya no como transformacion efimera en memoria del lado local.

Debe persistirse de forma estable.

### Campos persistidos objetivo

`youtube_playlist_item` ya dispone de:

* `normalized_title`
* `normalized_artist`

`local_song` debe añadir:

* `normalized_title`
* `normalized_artist`

El adaptador hacia el contrato comparable debe mapear ambos lados a:

* `comparable_title`
* `comparable_artist_full`
* `comparable_artist_primary`
* `comparable_artist_collaborators` cuando exista

Con esta decision:

* `normalized_*` sigue siendo un nombre de persistencia valido
* `comparable_*` pasa a ser el nombre semantico del contrato de matching

### Regla funcional

Queda eliminada la dependencia funcional de comparar:

* YouTube normalizado

contra:

* local sin normalizar

El flujo correcto pasa a comparar siempre:

* comparable YouTube normalizado
* comparable local normalizado

La validacion de artista ya no depende de igualdad exacta del artista completo.

Regla vigente:

* primero se valida el titulo exacto normalizado
* despues el artista ya no se decide por igualdad estricta del string completo
* el selector clasifica la validacion artistica al menos en `STRONG`, `MEDIUM` y `NONE`
* solo las candidatas con artista `STRONG` pasan al matcher activo
* las candidatas `MEDIUM` pueden servir como diagnostico, pero no abren `FOUND`
* las candidatas `NONE` se descartan siempre

Regla funcional del selector artistico:

* `STRONG`
  * `playlist primary == local primary`
  * o `playlist primary` coincide claramente con el bloque principal local
* `MEDIUM`
  * `playlist primary` aparece dentro del `artist full` local, pero no queda claro que sea principal
* `NONE`
  * artista realmente distinto

Los colaboradores solo pueden aportar evidencia secundaria y nunca abrir por si solos un `FOUND`.

### Regla estable de normalizacion del artista principal

Para tags locales:

* `feat`, `ft` y `featuring` cortan el bloque principal
* todo lo que quede antes de ese bloque es `artista principal`
* todo lo que quede despues pasa a `collaborators`
* el artista completo normalizado se conserva para trazabilidad

Para playlist:

* primero se usa la heuristica actual de extraccion desde YouTube
* el artista inferido desde el titulo o el canal se normaliza
* sobre ese valor ya normalizado se separa `primary` y `collaborators`
* si el caso real indica un artista base unico, no se mezclan colaboradores dentro del `primary`

Decision explicita sobre varios artistas sin marcador `feat`:

* si los artistas vienen unidos por `&`, `and`, `y`, coma, `+`, `x` o separadores equivalentes pero sin `feat/ft/featuring`, todo ese bloque se considera `artista principal multiple`
* en esos casos `collaborators` queda vacio

Ejemplos cerrados:

* `Cruz Cafune ft. West Dubai`
  * `primary`: `cruz cafune`
  * `full`: `cruz cafune west dubai`
  * `collaborators`: `west dubai`
* `SFDK & Mama San`
  * `primary`: `sfdk mama san`
  * `full`: `sfdk mama san`
  * `collaborators`: vacio
* `Natos y Waor, Recycled J`
  * `primary`: `natos y waor recycled j`
  * `full`: `natos y waor recycled j`
  * `collaborators`: vacio

### Ejemplos de validacion de artista

Caso valido:

* playlist: `Cruz Cafune`
* local: `Cruz Cafune ft. West Dubai`
* resultado: valido
* motivo: el artista principal de playlist coincide con el artista principal local aunque el local tenga colaboradores

Caso invalido:

* playlist: `SFDK`
* local: `Eazyboi`
* resultado: invalido
* motivo: el artista principal no coincide y no puede salir `FOUND`

## Estados funcionales

### `FOUND`

Se usa cuando:

* titulo y artista ya han quedado validados
* la candidata local es defendible
* no hay ambigüedad irresoluble

Regla dura:

* no puede existir `FOUND` con artista no validado
* no puede existir `FOUND` con artista realmente incorrecto aunque el titulo coincida
* en titulos genericos como `intro`, `outro`, `skit`, `interludio` y similares no basta el titulo; la duracion debe ayudar a confirmar

### `POSSIBLE_MATCH`

Se usa solo cuando:

* titulo y artista ya validaron una o mas candidatas
* el score final no puede romper la ambigüedad de forma segura
* o la mejor candidata validada no alcanza confirmacion automatica pero sigue siendo la opcion mas plausible entre varias equivalentes

No es una salida válida para artistas incorrectos.

### `MISSING`

Se usa cuando:

* no existe titulo en local
* existe titulo pero no artista principal valido
* existe artista parecido solo por colaboradores o ruido, pero no valida el artista principal
* tras exclusiones ya no queda candidata util
* no hay base suficiente para una decision defendible

## Score

El score:

* no abre la competicion
* no sustituye filtros duros
* no legitima artistas incorrectos

Solo sirve para:

* evaluar duracion
* confirmar consistencia
* desempatar candidatas validas

En el matcher vigente el score ya no valora ruido textual de pools amplios.

Solo puntua:

* duracion
* consistencia de una candidata ya validada
* desempate entre varias candidatas con el mismo titulo y artista

El matcher ya no decide el acceso al subconjunto.

Su responsabilidad queda reducida a:

* puntuar candidatas que ya han pasado `titulo -> artista -> reserva`
* trabajar solo con candidatas de titulo validado y artista `STRONG`
* resolver si una unica candidata queda en `FOUND`
* marcar `POSSIBLE_MATCH` cuando varias candidatas validas siguen siendo ambiguas
* no inferir artista desde ruido, containment debil ni colaboradores secundarios

No forma parte del flujo vigente ningun ruleset generico de score textual sobre pools amplios.

## Reserva de canciones locales

Reglas activas:

* una `local_song` en `FOUND` queda reservada
* una `local_song` reservada no vuelve a competir en la misma comparacion
* `POSSIBLE_MATCH` no reserva
* `MISSING` no reserva
* primero se siembran las reservas procedentes de `FOUND` congelados del snapshot valido
* despues la comparacion avanza en orden de playlist y cada `FOUND` nuevo estrecha el pool para los items siguientes

Esto reduce ruido y evita duplicar una misma cancion local en dos `FOUND`.

## Snapshot persistido

La comparacion persiste:

### `playlist_comparison`

Cabecera de snapshot con:

* scope de playlist y carpeta local
* marcas temporales de snapshot
* fingerprints de estado
* version de reglas

### `playlist_comparison_result`

Detalle por item con:

* `match_status`
* `local_song_id`
* `score`
* `matched_by`

## Incrementalidad

Reglas activas:

* `FOUND` validos pueden congelarse
* su `local_song_id` queda reservada
* la recomparacion incremental trabaja sobre filas nuevas, `MISSING`, `POSSIBLE_MATCH` y `FOUND` invalidados
* un `FOUND` valido no se reabre solo porque aparezca una candidata aparentemente mejor
* cualquier snapshot con `matching_rules_version` distinta a la vigente queda invalidado para congelacion automatica
* cualquier cambio de `matching_rules_version` invalida la congelacion automatica anterior
* el cambio de semantica del artista principal obliga a invalidar `FOUND` congelados calculados con reglas rigidas anteriores

## Razones legibles

Razones mínimas esperadas:

* `No existe titulo en local.`
* `Existe titulo pero no artista principal valido.`
* `La cancion local ya esta reservada por otro FOUND.`
* `Varias candidatas del mismo titulo y artista valido.`
* `Duracion dudosa entre candidatas validas.`
* `Coincidencia confirmada por titulo y artista validos.`

La evidencia `MEDIUM` puede registrarse para diagnostico, pero no debe mostrarse como razon final por defecto.

## Aplicacion y UI

### Caso de uso

`CompareYoutubePlaylistWithLocalLibraryUseCase` coordina:

* carga de playlist activa
* carga de biblioteca local activa
* preparacion de comparables
* construccion del indice normalizado por titulo
* validacion semantica de artista sobre el subconjunto del titulo
* matching
* reserva incremental de `FOUND`
* persistencia del snapshot
* devolucion de DTOs con resumen, items y observabilidad

El filtro artistico del flujo principal debe respetar siempre:

* un artista principal valido con colaboradores locales no debe caer en `MISSING`
* un artista distinto real no puede colarse como `FOUND`

El flujo principal debe mantenerse unico y lineal:

1. preparar comparables
2. construir indice normalizado por titulo
3. recorrer la playlist en orden
4. reutilizar `FOUND` congelados validos si existen
5. aplicar selector secuencial para el resto
6. validar artista de forma semantica dentro del subconjunto del titulo
7. reservar solo nuevos `FOUND`
8. persistir snapshot

### Indice de candidatas

El indice activo del selector no decide por `title + artist`.

Contrato vigente:

* el indice duro solo agrupa `local_song` por `title` normalizado
* el artista se resuelve despues, dentro del subconjunto recuperado por titulo
* no existe decision funcional rigida por `local_song_ids_by_title_artist`
* si en algun momento se reintroduce una optimizacion por `title + artist`, debe ser solo secundaria y nunca puede sustituir la validacion semantica de artista

### Pantalla de comparacion

La UI debe:

* hidratar snapshot persistido
* permitir `Refrescar snapshot`
* permitir `Recomparar pendientes`
* permitir `Recomparar todo`
* mostrar estado del snapshot
* mostrar motivos legibles
* permitir override manual sobre el snapshot actual

## Regla documental

Este documento sustituye como referencia viva la documentacion fragmentada de comparación.

Si aparece un documento antiguo que contradice este flujo, prevalece este documento.

## Persistencia y versionado

En esta fase no cambian los campos comparables persistidos en `local_song` ni en `youtube_playlist_item`.

Por tanto:

* no hace falta migracion nueva de esquema
* no hace falta backfill adicional sobre `normalized_title` y `normalized_artist`
* la invalidacion explicita de snapshots antiguos se resuelve subiendo `matching_rules_version`
