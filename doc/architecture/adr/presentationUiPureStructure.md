# Simplificacion de presentation hacia estructura UI pura

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobado.

## Contexto

La capa `app/presentation/` ya estaba bien separada por responsabilidades, pero seguia usando nombres internos como `shell/`, `shared/` y `features/*/viewmodel/` que no reflejaban con claridad una lectura de UI pura.

El objetivo de esta fase es acercar la estructura visible a:

```txt
app/presentation/
├─ windows/
├─ dialogs/
├─ widgets/
├─ viewmodels/
└─ styles/
```

sin perder el valor del enfoque por features para las pantallas funcionales.

## Decision

Se adopta una estructura hibrida:

```txt
app/presentation/
├─ features/
│  └─ <feature>/
│     ├─ controller/
│     └─ ui/
├─ windows/
├─ dialogs/
├─ widgets/
├─ viewmodels/
│  └─ <feature>/
└─ styles/
```

Cambios aplicados:

* `shell/` pasa a `windows/`
* `shared/widgets/` pasa a `widgets/`
* `shared/theme/` pasa a `styles/`
* `features/*/viewmodel/` pasa a `viewmodels/<feature>/`
* `dialogs/` se crea como paquete preparado para modales futuros
* se elimina `ui/` porque ya no tenia consumidores
* se eliminan `shared/` y `shell/` tras migrar todos los imports

## Criterios

* `features/` queda reservado para UI y controladores especificos de cada modulo visual
* `viewmodels/` concentra el estado y la coordinacion de UI por feature
* `widgets/` contiene componentes reutilizables transversales
* `styles/` centraliza tema, señales visuales, factory de widgets y estilo de ventana
* `windows/` contiene `MainWindow`, `AppShell` y piezas estructurales del escritorio

## Consecuencias

Ventajas:

* la capa `presentation` se lee con nomenclatura mas cercana a UI de escritorio
* se mantiene la modularidad por feature donde aporta mas claridad
* los imports de bootstrap y controllers quedan mas estables

Tradeoff:

* no se elimina `features/` porque sigue siendo la mejor unidad de agrupacion para pantallas especificas del producto
