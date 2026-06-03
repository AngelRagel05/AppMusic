# ADR: Persistencia concreta para canciones locales

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

El modelo `local_song` ya existia en:

* ORM SQLAlchemy
* migracion inicial
* documentacion de BBDD

La fase pendiente era exponer una implementacion concreta de persistencia para el dominio `LocalSong`.

## Decision

Se introduce `LocalSongSqlAlchemyRepository` en `app/infrastructure/persistence/repositories/`.

Comportamiento inicial:

* `list_by_folder(local_folder_id)`
* `get_by_file_path(file_path)`
* `save(local_song)`

La operacion `save(...)` funciona como `upsert` por `file_path`, aprovechando la unicidad global ya definida para `local_song.file_path`.

## Consecuencias

Ventajas:

* la futura fase de escaneo ya dispone de un repositorio concreto
* se reutiliza la unicidad objetiva ya fijada en BBDD
* no hace falta tocar migraciones ni esquema en esta fase porque `local_song` ya estaba alineado

Coste:

* el enriquecimiento de metadata completa sigue fuera de esta fase
