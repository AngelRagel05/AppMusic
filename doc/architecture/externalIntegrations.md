# Integraciones externas

## Integraciones actuales en dependencias

### Persistencia

* `SQLite`
* `SQLAlchemy`
* `Alembic`

Estado actual:

* la persistencia real esta agrupada en `app/infrastructure/persistence/`
* la configuracion principal sale de `DATABASE_URL`

### Descargas

* `yt-dlp`
* `ffmpeg-python`
* binario `ffmpeg`

Estado actual:

* existe la agrupacion `app/infrastructure/downloads/`
* `FFMPEG_PATH` ya es configurable en settings
* todavia no hay adaptadores funcionales relevantes implementados en codigo productivo

### Metadata

* `Mutagen`

Estado actual:

* existe `app/infrastructure/metadata/` como espacio reservado
* todavia no hay adaptadores funcionales relevantes implementados en codigo productivo

### Audio

* el objetivo arquitectonico contempla `pygame`

Estado actual:

* existe `app/infrastructure/audio/` como espacio reservado
* no hay integracion activa implementada todavia

### Red y utilidades tecnicas

* `httpx`
* `python-dotenv`
* `loguru`

Uso actual:

* `python-dotenv` carga configuracion desde entorno
* `loguru` se usa a traves de `app/shared/utils/logging.py`
* `httpx` queda disponible para futuras integraciones externas

## Reglas de encapsulacion

* ninguna ventana o widget debe hablar directamente con estas librerias
* los adaptadores concretos deben vivir en `app/infrastructure/`
* `application/` solo debe depender de contratos o protocolos cuando haga falta
* `domain/` no debe conocer estas librerias

## Documentos relacionados

* [infrastructureAdapterReorganization.md](./infrastructureAdapterReorganization.md)
* [layerDependencyRules.md](./layerDependencyRules.md)
