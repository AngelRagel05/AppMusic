# Contexto del Sistema

## Objetivo

Este documento unifica la arquitectura base del proyecto y sustituye la documentacion dispersa sobre capas, dependencias, modulos de dominio e integraciones.

## Arquitectura base

El proyecto sigue una arquitectura limpia ligera con estas capas:

```txt
app/
├─ bootstrap/
├─ presentation/
├─ application/
├─ domain/
├─ infrastructure/
├─ shared/
├─ workers/
└─ config/
```

Flujo principal:

```txt
UI -> Controller/ViewModel -> UseCase -> Domain -> Repository/Infrastructure
```

## Responsabilidades por capa

### `presentation`

Responsable de:

* ventanas
* widgets
* dialogs
* controllers
* viewmodels
* estilos y helpers visuales

No debe contener logica de negocio pesada ni acceso directo a infraestructura.

### `application`

Responsable de:

* use cases
* DTOs
* validadores de entrada

Orquesta acciones del sistema sin conocer detalles de UI ni implementaciones concretas.

### `domain`

Responsable de:

* entidades
* servicios de dominio
* contratos de repositorio
* reglas puras de negocio

No depende de frameworks ni adaptadores externos.

### `infrastructure`

Responsable de:

* persistencia
* filesystem
* metadata
* integraciones externas
* adaptadores tecnicos

Implementa contratos definidos en capas superiores.

### `shared`

Responsable de:

* constantes comunes
* excepciones compartidas
* utilidades transversales

No debe convertirse en una capa comodin para mezclar responsabilidades.

### `bootstrap`

Responsable de:

* composition root
* construccion y cableado de dependencias

### `workers`

Responsable de:

* tareas pesadas en segundo plano
* coordinacion no bloqueante de procesos largos

## Modulos de dominio

### `library`

Agrupa:

* `LocalFolder`
* `LocalSong`
* contratos de repositorio de biblioteca local

### `playlists`

Agrupa:

* `YoutubePlaylist`
* `YoutubePlaylistItem`
* contratos y servicios de comparacion

### `filters`

Agrupa:

* `IgnoredTerm`
* reglas de terminos ignorados

### Modulos previstos

* `downloads`
* `metadata`
* `playback`

## Reglas de dependencia

Reglas activas:

* `presentation` depende de `application`
* `application` depende de `domain`
* `domain` no depende de `presentation` ni de `infrastructure`
* `infrastructure` implementa contratos de `domain`
* `bootstrap` puede conocer todas las capas para componerlas
* `workers` coordinan use cases y adaptadores sin romper el limite de capas

## Integraciones externas

Integraciones activas o previstas:

* SQLite mediante SQLAlchemy
* filesystem local
* Mutagen para metadata de MP3
* `yt-dlp` para importacion/descarga de YouTube
* `ffmpeg` para operaciones de audio cuando aplique

Todas deben quedar aisladas en `infrastructure`.

## Contextos documentales derivados

La documentacion funcional y tecnica detallada del sistema queda agrupada en:

* [youtubePlaylistContext.md](./youtubePlaylistContext.md)
* [localLibraryContext.md](./localLibraryContext.md)
* [comparisonContext.md](./comparisonContext.md)
* [presentationContext.md](./presentationContext.md)
* [runtimeAndQualityContext.md](./runtimeAndQualityContext.md)

