# Reorganizacion de infrastructure por adaptadores reales

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobado.

## Contexto

La capa `app/infrastructure/` mezclaba persistencia SQLAlchemy con carpetas tematicas al mismo nivel, usando `database/` y `repositories/` como nombres tecnicos demasiado genericos.

El objetivo de esta fase es que la infraestructura quede agrupada por tipo de integracion real:

* persistencia
* audio
* descargas
* metadata
* configuracion
* logging

## Decision

Se reorganiza la infraestructura hacia esta estructura:

```txt
app/infrastructure/
├─ persistence/
│  ├─ database/
│  └─ repositories/
├─ audio/
├─ downloads/
│  └─ youtube/
├─ metadata/
├─ config/
└─ logging/
```

Cambios aplicados:

* `app/infrastructure/database/` pasa a `app/infrastructure/persistence/database/`
* `app/infrastructure/repositories/` pasa a `app/infrastructure/persistence/repositories/`
* se crea `app/infrastructure/persistence/__init__.py` como punto de entrada estable para bootstrap y tests
* `app/infrastructure/youtube/` pasa a `app/infrastructure/downloads/youtube/`
* se crean `config/` y `logging/` como paquetes preparados para futuros adaptadores
* se elimina `filesystem/` porque estaba vacio, no tenia consumidores y no forma parte del mapa objetivo de esta fase

## Criterios

* `persistence/` contiene SQLAlchemy, sesion, modelos ORM, bootstrap de base de datos y repositorios concretos
* `downloads/` agrupa integraciones de descarga como YouTube, `yt-dlp` y `ffmpeg`
* `audio/` queda reservado para `pygame` o adaptadores equivalentes
* `metadata/` queda reservado para adaptadores `Mutagen`
* `config/` y `logging/` concentran adaptadores tecnicos transversales de infraestructura

## Consecuencias

Ventajas:

* la infraestructura queda alineada con responsabilidades tecnicas reales
* bootstrap y tests consumen una API mas clara a traves de `app.infrastructure.persistence`
* se reduce la ambiguedad de carpetas tecnicas genricas

Limitaciones actuales:

* `audio/`, `downloads/`, `metadata/`, `config/` y `logging/` quedan preparados pero todavia casi vacios
* no se han introducido adaptadores falsos; solo se ha movido y normalizado lo que ya existia realmente
