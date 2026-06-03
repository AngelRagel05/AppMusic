# Presentation MVC

## Objetivo

Definir como se aplica MVC en la capa `presentation/` del proyecto.

---

## Regla de reparto

La capa de presentacion debe organizarse asi:

* `app/presentation/shell/`
  contiene ventana principal, layout y navegacion global
* `app/presentation/shared/`
  contiene tema, widgets y soporte visual reutilizable
* `app/presentation/features/`
  contiene modulos funcionales de presentacion agrupados por feature

---

## Criterio practico

### View

La vista:

* crea widgets
* define layout
* aplica tema y estilos de `Tkinter`
* expone metodos de lectura y renderizado de estado visual
* encapsula la lectura y escritura de sus propios widgets internos

No debe:

* ejecutar casos de uso
* decidir flujos de interaccion
* acceder a infraestructura

### Controller

El controlador:

* conecta senales de la vista
* decide el flujo de cada accion del usuario
* llama a `viewmodels`
* actualiza la vista con los resultados
* maneja mensajes y validaciones de interaccion

### Model

En este proyecto, el papel de modelo en presentation se apoya en:

* `viewmodels/` como adaptadores de presentacion
* `application/use_cases/` como entrada de acciones
* DTOs como datos de intercambio

No se introduce un ORM ni entidades de dominio dentro de `presentation`.

---

## Estructura objetivo

```txt
app/presentation/
├─ shell/
│  ├─ mainWindow/
│  └─ appShell/
├─ shared/
│  ├─ theme/
│  ├─ widgets/
│  └─ events/
└─ features/
   ├─ overview/
   ├─ localLibrary/
   ├─ youtubePlaylists/
   └─ ignoredTerms/
```

---

## Decision tecnica

Se mantiene un MVC ligero en `presentation`, pero organizado por feature:

* `shell/` resuelve composicion, ventana y navegacion
* cada feature agrupa su `ui`, su `controller` y su `viewmodel`
* `shared/` centraliza solo elementos reutilizables de presentacion
* `MainWindow` y el layout global no deben coordinar casos de uso directamente

La ADR de referencia para esta organizacion es:

* `doc/architecture/feature_modular_presentation_tkinter.md`
