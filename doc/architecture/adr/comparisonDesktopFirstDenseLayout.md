# Comparison Desktop-First Dense Layout

## Contexto

La pantalla `Comparacion` estaba usando:

* tarjetas grandes por cancion
* KPIs altos con mucho padding
* controles de filtro y paginacion de tamaño casi formulario

Eso hacia que la densidad de informacion visible fuera demasiado baja para una herramienta de escritorio.

## Decision

La pantalla `Comparacion` pasa a un layout `desktop first` mas compacto inspirado en herramientas de escritorio orientadas a productividad.

Cambios principales:

* listas de canciones y resultados en filas compactas con separadores finos
* bloque de resumen unificado en lugar de tarjetas KPI individuales
* buscador y filtro en formato horizontal compacto
* paginacion con botones pequenos y menos padding
* radios, margenes y espaciados reducidos

## Motivos

* aumentar la cantidad de informacion visible por pantalla
* reducir espacio muerto y sensacion de dashboard web
* acercar la UX a herramientas tipo Spotify Desktop, Steam o VS Code

## Consecuencias

* la pantalla muestra significativamente mas canciones por viewport
* la jerarquia visual depende mas de tipografia y separadores que de tarjetas
* el tema de `Comparacion` usa overrides especificos para radios y alturas mas compactas
