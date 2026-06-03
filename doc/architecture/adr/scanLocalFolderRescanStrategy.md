# ADR: Estrategia de reescaneo de biblioteca local v1

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La primera version del escaneo local ya tiene definido su alcance:

* recorrer la carpeta local activa
* detectar archivos `.mp3`
* registrar canciones locales en base de datos

Faltaba fijar de forma explicita que debe ocurrir cuando el usuario vuelve a escanear una biblioteca ya escaneada, para evitar ambiguedad entre:

* duplicar canciones ya existentes
* actualizar registros existentes
* eliminar canciones que ya no esten en disco

## Decision

En v1, el reescaneo sigue una estrategia determinista de `upsert` por `file_path`.

Esto implica:

* si un archivo ya existe por `file_path`, no se duplica
* si aparece un archivo nuevo, se crea su registro
* si un archivo desaparece del disco, no se borra en v1

La politica operativa de v1 es conservadora:

* solo detectar y registrar nuevos archivos
* reutilizar el registro existente cuando el `file_path` ya esta persistido
* no aplicar todavia limpieza de ausentes ni marcado de huella de borrado

## Relacion con persistencia

Esta decision se apoya en la unicidad global de `local_song.file_path` y en el comportamiento `upsert` ya definido en `LocalSongSqlAlchemyRepository`.

## Consecuencias

Ventajas:

* el reescaneo es idempotente respecto a la misma ruta
* no se generan duplicados por volver a lanzar el escaneo
* la primera iteracion sigue siendo simple de probar y razonar

Costes:

* los archivos ausentes seguiran presentes en base de datos hasta una fase posterior
* la limpieza de biblioteca requerira una historia separada

## Fuera de alcance

En esta fase no se implementa:

* borrado fisico o logico de canciones ausentes
* deduplicacion por fingerprint
* reconciliacion avanzada entre rutas movidas o renombradas
