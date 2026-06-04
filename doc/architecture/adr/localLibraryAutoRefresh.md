# ADR: Auto-refresh de biblioteca local por monitorizacion de carpeta

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

El escaneo manual ya permitia:

* registrar canciones nuevas
* refrescar metadata
* detectar ausentes o movidas durante un reescaneo

Pero la app no reflejaba cambios automaticamente mientras estaba abierta.

Si el usuario:

* copiaba un MP3
* borraba un MP3
* movia un MP3 dentro de la biblioteca activa

debia lanzar el escaneo manualmente para ver el cambio en la app.

## Decision

Se introduce auto-refresh de la biblioteca local mientras la app esta abierta.

La solucion se divide en dos piezas:

* `LocalFolderSnapshotReader` en `app/infrastructure/filesystem/`, responsable de capturar una firma ligera del estado actual de los MP3 de la carpeta activa
* `LocalFolderMonitorWorker` en `app/workers/`, responsable de vigilar esa firma en segundo plano y disparar un nuevo escaneo cuando cambie

La monitorizacion:

* observa solo la carpeta local activa
* funciona por polling con intervalo fijo
* no bloquea la UI
* reusa el caso de uso de escaneo existente para mantener una sola fuente de sincronizacion

## Consecuencias

Ventajas:

* la app refleja cambios de disco sin accion manual del usuario
* la UI no incorpora acceso directo a filesystem
* el refresco automatico reutiliza la logica ya probada de escaneo local

Costes:

* el polling no es instantaneo; depende del intervalo configurado
* una rafaga de cambios puede disparar varios reescaneos sucesivos
* no se usa notificacion nativa del sistema de archivos en esta fase

## Fuera de alcance

En esta fase no se implementa:

* integracion con `watchdog` o APIs nativas del sistema operativo
* debounce avanzado por lotes de eventos
* monitorizacion simultanea de varias carpetas activas
