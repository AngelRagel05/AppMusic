# ADR: Deteccion de canciones ausentes o movidas en escaneo local

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

El escaneo local ya:

* registraba canciones nuevas
* refrescaba metadata de canciones existentes
* evitaba duplicados por `file_path`

Pero seguia sin resolver que hacer cuando una cancion:

* desaparecia del disco
* cambiaba de carpeta dentro de la misma biblioteca local

Eso dejaba filas obsoletas en `local_song` sin ninguna senal operativa para distinguir:

* canciones realmente disponibles
* canciones ausentes
* canciones movidas que debian reconciliarse

## Decision

Se introduce seguimiento de disponibilidad en `local_song` mediante `is_available`.

Durante cada escaneo:

* si el archivo aparece en la misma ruta, se actualiza su metadata y queda `is_available = true`
* si aparece una ruta nueva, se intenta reconciliar con canciones ausentes de la misma carpeta
* si la reconciliacion encuentra una unica coincidencia por `file_name` y metadata basica, se actualiza el `file_path` existente
* si una cancion persistida ya no aparece y no puede reconciliarse, se marca `is_available = false`

La reconciliacion de movidas es deliberadamente conservadora.

La coincidencia exige:

* mismo `file_name`
* mismo `title`
* mismo `artist`
* mismo `album`
* mismo `release_year`
* mismo `track_number_album`
* misma `duration_seconds` redondeada a una decimal

Si hay cero o varias coincidencias posibles, la app no fuerza reconciliacion automatica.

## Consecuencias

Ventajas:

* la app distingue canciones disponibles de canciones ausentes
* los movimientos simples entre carpetas quedan reconciliados sin duplicar filas
* la deteccion sigue siendo trazable y facil de probar

Costes:

* las movidas con renombrado o con metadata alterada pueden no reconciliarse
* la estrategia sigue sin usar fingerprint de audio

## Fuera de alcance

En esta fase no se implementa:

* fingerprint acustico
* deteccion robusta de renombrados
* reconciliacion entre carpetas distintas guardadas como bibliotecas separadas
* borrado fisico de filas de `local_song`
