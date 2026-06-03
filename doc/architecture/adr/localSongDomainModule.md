# ADR: Introduccion del modulo de dominio para canciones locales

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La base de datos y el modelo ORM ya contemplan `local_song`, pero el dominio modular de `library` todavia no exponia una entidad ni un contrato explicito para representar canciones locales detectadas dentro de una biblioteca.

Eso dejaba incompleta la base del futuro flujo de escaneo de MP3.

## Decision

Se introduce el minimo dominio necesario dentro de `app/domain/library/`:

* entidad `LocalSong`
* contrato `LocalSongRepository`
* servicio minimo `normalizeLocalSongFilePath(...)`

La regla de modelado queda fijada asi:

* `LocalFolder` representa la biblioteca local
* `LocalSong` representa cada MP3 detectado dentro de esa biblioteca

## Consecuencias

Ventajas:

* el dominio queda alineado con el modelo relacional ya documentado
* la futura implementacion del escaneo puede apoyarse en contratos claros
* se mantiene la modularidad por contexto `library`

Coste:

* todavia no hay caso de uso ni repositorio concreto de escaneo en esta fase
