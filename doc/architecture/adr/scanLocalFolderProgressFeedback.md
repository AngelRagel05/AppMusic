# ADR: Progreso visible durante el escaneo local

## Estado

Aprobada

## Fecha

2026-06-04

## Contexto

El escaneo local ya se ejecutaba en segundo plano y devolvia un resumen final al terminar.

Eso evitaba bloquear la interfaz, pero durante escaneos largos el usuario solo veia un estado generico de espera.

Faltaba una senal visible de avance para responder preguntas operativas como:

* cuantas canciones lleva procesadas
* cuantas faltan por revisar
* si el escaneo sigue avanzando o parece detenido

## Decision

Se introduce progreso incremental en el flujo de escaneo local.

La solucion:

* define `ScanLocalFolderProgressDto` como contrato de progreso
* emite progreso desde `ScanLocalFolderUseCase` al inicio y tras procesar cada MP3 detectado
* propaga ese progreso a traves de `ScanLocalFolderWorker`
* actualiza la UI con un contador visible `procesadas/total canciones`

Se prioriza el contador absoluto frente a un porcentaje porque comunica mejor el volumen real de trabajo durante escaneos largos.

## Consecuencias

Ventajas:

* el usuario ve avance real sin bloquear la interfaz
* el progreso reutiliza el worker y el hilo principal ya existentes
* no hace falta introducir barras de progreso ni estado extra de persistencia

Costes:

* el progreso refleja canciones procesadas, no tiempo restante estimado
* el total solo contempla MP3 detectados, no operaciones internas posteriores

## Fuera de alcance

En esta fase no se implementa:

* porcentaje visual
* ETA o tiempo restante estimado
* progreso persistido entre sesiones
