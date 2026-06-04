# LocalMusicScanner en infrastructure

Estado: historico

Si entra en conflicto con la documentacion canonica, prevalece la documentacion canonica.

## Contexto

La historia de escaneo de biblioteca local necesita una pieza tecnica que descubra archivos MP3 en disco sin mezclar UI ni persistencia.

## Decision

Se introduce `LocalMusicScanner` en `app/infrastructure/filesystem/localMusicScanner.py`.

Su responsabilidad en v1 es:

* recorrer recursivamente una carpeta dada
* detectar archivos con extension `.mp3` de forma case-insensitive
* devolver rutas absolutas ya resueltas
* ignorar archivos o subrutas no accesibles sin interrumpir todo el escaneo
* fallar de forma explicita si la carpeta raiz ya no existe o no puede leerse

`LocalMusicScanner` no:

* toca widgets o viewmodels
* persiste resultados en base de datos
* crea metadata avanzada con `Mutagen`
* aplica deduplicacion avanzada por huella

## Consecuencias

* el descubrimiento de archivos queda encapsulado en `infrastructure`
* el futuro `ScanLocalFolderUseCase` podra reutilizar este adaptador sin depender de `os.walk` o `pathlib`
* el flujo de aplicacion puede distinguir entre una carpeta vacia y una carpeta invalida o inaccesible
* los errores de la carpeta raiz se convierten en mensajes claros para la UI, mientras que las subrutas inaccesibles se mantienen como warnings tolerados
