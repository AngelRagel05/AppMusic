# Contexto de Presentacion

## Objetivo

Unificar la documentacion sobre estructura de `presentation`, shell, features, MVC ligero y reglas visuales de escritorio.

## Estructura canónica

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

## Responsabilidades

### `windows`

Contiene:

* `MainWindow`
* shell global
* sidebar
* composicion general

### `features`

Cada feature agrupa su UI propia y sus controladores.

Features principales:

* overview
* localLibrary
* youtubePlaylists
* comparison
* ignoredTerms

### `dialogs`

Ventanas auxiliares y modales.

### `widgets`

Componentes visuales compartidos.

### `viewmodels`

Estado y coordinacion ligera de presentacion por feature.

### `styles`

Paleta, factories visuales y helpers comunes.

## MVC ligero

### View

* crea widgets
* define layout
* renderiza estado

### Controller

* conecta eventos
* decide flujo de interaccion
* llama a viewmodels

### ViewModel

* mantiene estado de presentacion
* llama a use cases
* no implementa logica de negocio pesada

## Reglas de UI

* la UI debe sentirse como app de escritorio
* usar Tkinter y preferentemente CustomTkinter
* no introducir paradigmas web
* centralizar tema y estilos
* mantener densidad visual y claridad funcional
* no ejecutar trabajo pesado en el hilo principal

La guia visual detallada se mantiene en:

* [../ui/uiUxGuidelines.md](../ui/uiUxGuidelines.md)

## Pantalla de comparacion

La feature de comparación debe:

* trabajar con snapshot persistido
* renderizar estados `FOUND`, `POSSIBLE_MATCH` y `MISSING`
* mostrar razones legibles
* permitir acciones de refresh, recomparacion y override manual

