# ADR: Pantalla dividida para detalle de biblioteca local y playlist importada

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

La aplicacion ya podia importar items de la playlist activa y escanear canciones de la biblioteca local activa, pero no existia una vista dedicada para inspeccionar ambos conjuntos de datos en paralelo.

## Decision

Se añade una nueva pantalla `Comparacion` en el aside izquierdo.

La vista divide el contenido en dos columnas:

* izquierda: canciones disponibles del `local_folder` activo
* derecha: items importados de la `youtube_playlist` activa

La UI no compara todavia por score ni muestra matching; solo expone el detalle de ambos lados para preparar la fase de comparacion funcional.

## Consecuencias

Ventajas:

* el usuario puede inspeccionar rapidamente ambos conjuntos de datos
* se reutilizan casos de uso de lectura en application, sin acceder a persistencia desde UI
* la pantalla sirve como base visual para la comparacion futura

Limitaciones:

* todavia no hay emparejamiento ni resaltado de coincidencias
* la ordenacion actual depende de los repositorios existentes
