# Loading Overlays For Initial And Comparison Flows

## Contexto

Aunque se hayan reducido cuellos de botella reales, la app sigue teniendo momentos donde la UI necesita tiempo para:

* cargar estado inicial
* montar la pantalla de comparacion
* esperar a tareas en background

Sin una capa visual de carga, el usuario percibe mezcla de pantallas, repintado parcial o una app rota.

## Decision

Se introducen overlays de carga opacos en dos puntos:

* arranque de la app
* carga de la pagina de comparacion cuando no hay cache valida

Los overlays se muestran antes de lanzar el trabajo costoso y se ocultan al terminar o al producirse error.

## Consecuencias

* la transicion visual queda controlada y no se ven pantallas mezcladas
* el usuario recibe feedback inmediato aunque siga existiendo latencia residual
* la solucion no sustituye la optimizacion real; solo mejora la percepcion y evita estados visuales rotos
