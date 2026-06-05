# Comparison Reason Visibility

## Contexto

La comparación ya calculaba un `reason` técnico por cada resultado, pero la interfaz no lo mostraba al usuario.

Eso impedía entender por qué una coincidencia habia sido considerada valida, parcial o insuficiente.

## Decision

La pantalla `Comparacion` muestra el motivo de matching en la segunda linea de cada resultado.

Formato:

* primera linea: cancion de YouTube y estado
* segunda linea: candidata local y resumen legible del motivo

El motivo se resume con una capa de presentacion para evitar textos demasiado técnicos o ruidosos.

## Consecuencias

* el usuario puede auditar por qué una coincidencia fue aceptada
* la decision de matching se vuelve mas explicable sin abrir paneles adicionales
* la interfaz mantiene un layout compacto de dos lineas por resultado
