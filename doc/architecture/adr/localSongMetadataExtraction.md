# ADR: Extraccion de metadata local con Mutagen

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

El escaneo local ya detectaba archivos MP3 y registraba rutas en `local_song`, pero no poblaba campos como:

* `title`
* `artist`
* `album`
* `release_year`
* `track_number_album`
* `duration_seconds`

Eso dejaba la tabla con valores vacios o por defecto aunque el esquema ya contemplaba metadata musical basica.

## Decision

Se introduce `MutagenLocalSongMetadataReader` en `app/infrastructure/metadata/`.

Su responsabilidad es:

* leer metadata basica de un MP3 con `Mutagen`
* devolver un `LocalSongMetadataDto`
* aplicar fallback seguro cuando falten tags o el archivo no pueda leerse

`ScanLocalFolderUseCase` pasa a usar este adaptador al registrar canciones nuevas detectadas durante el escaneo.

## Consecuencias

Ventajas:

* `local_song` queda poblada con metadata util desde el primer escaneo
* la integracion externa sigue encapsulada en `infrastructure`
* el `use case` conserva la coordinacion sin depender directamente de `Mutagen`

Costes:

* el escaneo incorpora una dependencia mas por archivo
* algunos MP3 sin tags seguiran usando valores de fallback
