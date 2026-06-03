# ADR: Alcance de escaneo local v1

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La aplicacion ya permite registrar y activar una biblioteca local, pero todavia no implementa el flujo real de escaneo de archivos musicales dentro de esa carpeta.

Antes de introducir casos de uso, workers, persistencia de canciones o adaptadores de filesystem, hace falta fijar el alcance funcional minimo de la primera version para evitar mezclar:

* deteccion basica de archivos
* enriquecimiento de metadata
* sincronizacion con servicios externos
* optimizaciones prematuras

## Decision

En la primera version, `escanear biblioteca local` significa unicamente:

* recorrer recursivamente la carpeta local activa
* detectar archivos con extension `.mp3`
* registrar esos archivos en base de datos

La operacion se considera completada cuando la app puede tomar la biblioteca local activa, inspeccionar su arbol de directorios y dejar persistidos los MP3 detectados como canciones locales registradas.

## Fuera de alcance en v1

Quedan explicitamente fuera de esta primera version:

* lectura profunda de metadata con `Mutagen`
* deduplicacion avanzada por huella o fingerprint
* sincronizacion con YouTube
* progreso fino por archivo

## Consecuencias

Ventajas:

* permite entregar primero un escaneo funcional y verificable
* reduce acoplamiento inicial entre filesystem, metadata y sincronizacion
* simplifica el testing de la primera iteracion

Costes:

* la informacion registrada en v1 sera deliberadamente basica
* el usuario no tendra todavia detalle fino del progreso ni enriquecimiento completo de canciones

## Nota de implementacion

Las siguientes fases deberan respetar este alcance:

* el descubrimiento de archivos vive en `infrastructure`
* la coordinacion del escaneo vive en `application`
* la UI solo dispara la accion y muestra resultados
* el reescaneo de v1 sigue una estrategia conservadora e idempotente documentada aparte: `upsert` por `file_path`, sin borrar ausentes
