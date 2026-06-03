# ADR: Limpieza de `shared` en la UI

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

Tras reorganizar `presentation` por `shell + shared + features`, todavia quedaban dos restos de la estructura anterior:

* `app/presentation/uiTheme/`
* `app/presentation/ui/shared/`

Ambos contenian utilidades reutilizables, pero su ubicacion ya no reflejaba la arquitectura aprobada.

## Decision

La infraestructura reutilizable de UI se centraliza en `app/presentation/shared/`.

Estructura objetivo:

```txt
app/presentation/shared/
├─ theme/
│  ├─ signalSupport.py
│  ├─ themePalette.py
│  ├─ widgetFactory.py
│  └─ windowStyler.py
└─ widgets/
   ├─ dataTable/
   ├─ pageHeader/
   ├─ statCard/
   └─ statusBadge/
```

### Reglas

* `shared/theme/` contiene paleta, factories, helpers de estilo y senales reutilizables
* `shared/widgets/` contiene solo componentes realmente compartidos entre varias features o el shell
* cualquier componente o helper especifico de una pantalla debe vivir dentro de la feature correspondiente

## Consecuencias

Ventajas:

* desaparecen paquetes legacy con nombre tecnico antiguo
* el codigo reutilizable queda en una sola zona coherente
* se reduce la tentacion de dejar helpers de pantalla fuera de su feature

Costes:

* hay que mantener criterio estricto para no volver a inflar `shared/`

## Nota operativa

Que algo sea pequeno no implica que deba vivir en `shared/`.

Solo entra en `shared/` si su reutilizacion entre varias features o el shell es real y estable.
