# Dashboard Layout

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Objetivo

Definir el patron visual de la pantalla principal para que se sienta como una app moderna de
escritorio y no como un formulario web empaquetado.

## Decision

La pantalla principal usa:

* sidebar izquierda fija para navegacion por zonas
* header superior con titulo, estados activos y acciones principales
* area central desplazable con cards amplias y limpias
* listas visuales para bibliotecas, playlists y terminos cuando el volumen es bajo

## Criterios visuales

* fondo base `#121212`
* capa lateral y paneles principales `#1B1B1B`
* superficies elevadas `#242424`
* rojo `#D64545` solo para accion principal
* azul `#5B8DEF` solo para informacion y estados
* padding interno de `16px` a `24px`
* titulos entre `20px` y `24px`
* subtitulos entre `13px` y `14px`
* texto normal entre `14px` y `15px`

## Reglas operativas

* cada seccion debe tener una unica accion principal evidente
* las acciones secundarias deben ir en menus contextuales discretos
* el feedback de una accion debe aparecer dentro de la seccion donde ocurre
* las listas pequenas deben resolverse con filas tipo card en lugar de tablas pesadas
