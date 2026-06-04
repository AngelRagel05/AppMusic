# ADR: Mensajes claros para carpetas locales inaccesibles

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

El escaneo de biblioteca local ya podia ejecutarse en segundo plano y mostrar progreso y resumen.

Sin embargo, cuando la carpeta activa desaparecia, dejaba de ser una carpeta valida o no podia leerse, el flujo no distinguia bien entre:

* una carpeta vacia
* una carpeta inexistente
* una carpeta sin permisos de lectura

Eso podia terminar mostrando `0 MP3 detectados` cuando en realidad habia un problema de acceso.

## Decision

Se separan los errores de acceso a la carpeta raiz del resto de incidencias tolerables del escaneo.

La solucion queda asi:

* `LocalMusicScanner` lanza error explicito si la carpeta raiz no existe
* `LocalMusicScanner` lanza error explicito si la carpeta raiz no puede leerse
* `ScanLocalFolderUseCase` traduce esos fallos a mensajes claros con el nombre visible y la ruta de la biblioteca
* la UI reutiliza esos mensajes sin inventar otra traduccion adicional

Se mantiene la tolerancia para subcarpetas o archivos individuales inaccesibles durante el recorrido, que siguen registrandose como warnings sin abortar todo el escaneo.

## Consecuencias

Ventajas:

* el usuario entiende por que el escaneo no puede continuar
* desaparece la confusion entre carpeta vacia y carpeta inaccesible
* la logica de deteccion tecnica sigue encapsulada en infraestructura

Costes:

* el contrato del scanner deja de ser completamente tolerante para la carpeta raiz
* el caso de uso necesita traducir errores tecnicos a mensajes funcionales

## Fuera de alcance

En esta fase no se implementa:

* recuperacion automatica de permisos
* selector automatico de una carpeta alternativa
* diagnostico detallado por subcarpeta inaccesible
