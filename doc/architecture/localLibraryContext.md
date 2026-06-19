# Contexto de Biblioteca Local

## Objetivo

Unificar la documentacion sobre carpeta local activa, escaneo de MP3, persistencia de canciones y actualizacion incremental de disponibilidad.

## Flujo funcional

1. el usuario define o activa una carpeta local
2. la app escanea el filesystem
3. descubre archivos MP3
4. extrae metadata con `Mutagen`
5. persiste o actualiza `local_song`
6. marca disponibilidad real y detecta ausencias o movimientos

## Persistencia principal

### `local_folder`

Guarda:

* ruta completa
* nombre visible
* estado activo

Regla operativa:

* solo una carpeta local puede estar activa al mismo tiempo

### `local_song`

Guarda:

* `file_path`
* `file_name`
* `title`
* `artist`
* `album`
* `release_year`
* `track_number_album`
* `duration_seconds`
* `is_available`
* enlaces opcionales a descarga
* y, desde Fase 2, campos comparables persistidos para matching

## Escaneo y reconciliacion

El escaneo local debe:

* descubrir MP3 actuales
* persistir altas nuevas
* detectar canciones ausentes
* reconciliar movimientos cuando haya evidencia suficiente
* no bloquear la interfaz

La disponibilidad de `local_song` forma parte de la verdad operativa de la comparacion.

## Metadata local

La metadata local debe producir datos comparables estables para el matching.

Reglas activas:

* el lado local no debe entrar crudo al flujo de comparacion
* la normalizacion debe ser simetrica con la de playlist
* el archivo MP3 sigue siendo la fuente real de metadata musical

### Decision de Fase 2

El lado local tambien debe persistir sus comparables.

Campos objetivo:

* `normalized_title`
* `normalized_artist`

Reglas:

* `title` y `artist` siguen siendo metadata visible del archivo
* `normalized_title` y `normalized_artist` pasan a ser la superficie persistida para matching
* cualquier cambio de metadata local relevante debe recalcular tambien esos campos comparables

## Casos de uso implicados

* definir carpeta local activa
* escanear carpeta local
* listar canciones activas
* rehidratar biblioteca persistida

## Relacion con comparacion

La comparacion consume `local_song` disponible y comparable.

No debe resolver dentro del matcher problemas que pertenecen al escaneo o a la extraccion de metadata.

La referencia funcional del matching vive en:

* [comparisonContext.md](./comparisonContext.md)
