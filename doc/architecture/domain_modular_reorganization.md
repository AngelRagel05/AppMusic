# ADR: Reorganizacion fisica de `domain/` por modulo

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

El mapa modular del dominio ya definia `library`, `playlists` y `filters` como modulos reales actuales.

Faltaba ejecutar la reorganizacion fisica del codigo para dejar de depender de carpetas globales por tipo tecnico como:

* `domain/entities/`
* `domain/repositories/`
* `domain/services/`

## Decision

Se reorganiza la capa `domain/` con estructura modular real:

```txt
app/domain/
├── library/
├── playlists/
├── filters/
├── downloads/
├── metadata/
└── playback/
```

### Modulos con contenido actual

* `library/`
  contiene `LocalFolder` y `LocalFolderRepository`
* `playlists/`
  contiene `YoutubePlaylist` y `YoutubePlaylistRepository`
* `filters/`
  contiene `IgnoredTerm` e `IgnoredTermRepository`

### Modulos preparados para evolucion futura

* `downloads/`
* `metadata/`
* `playback/`

Estos modulos se crean con la estructura interna prevista, pero sin llenarlos artificialmente con logica inexistente.

## Regla aplicada

Dentro de cada modulo:

```txt
<module>/
├── entities/
├── services/
├── actions/
├── repositories/
└── interfaces/
```

Restricciones:

* `services/` solo para logica de dominio real
* `repositories/` solo para contratos de persistencia
* `interfaces/` solo si una abstraccion externa aporta claridad real

## Ajuste adicional

Se elimina `BaseRepository` del dominio porque era una abstraccion tecnica generica usada solo por infraestructura.

El repositorio generico de SQLAlchemy deja de depender de un contrato global del dominio y queda como helper tecnico de infraestructura.

## Consecuencias

Ventajas:

* el dominio queda alineado con los modulos funcionales reales
* desaparecen carpetas globales ambiguas
* la nomenclatura se acerca mas a DDD light

Costes:

* hay que actualizar imports en `application`, `infrastructure` y tests

## Nota

Esta fase reorganiza `domain/`, pero no fuerza a crear servicios, actions o interfaces vacios con logica ficticia.

Su existencia estructural no implica que deban llenarse hasta que el modulo realmente lo necesite.
