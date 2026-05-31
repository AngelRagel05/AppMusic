# Presentation MVC

## Objetivo

Definir como se aplica MVC en la capa `presentation/` del proyecto.

---

## Regla de reparto

La capa de presentacion debe organizarse asi:

* `app/presentation/ui/`
  contiene vistas y componentes visuales
* `app/presentation/controllers/`
  contiene controladores de pantalla y coordinacion de eventos
* `app/presentation/viewmodels/`
  actua como fachada de presentacion hacia los use cases de `application`

---

## Criterio practico

### View

La vista:

* crea widgets
* define layout
* aplica QSS
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

## Ejemplo actual

```txt
app/presentation/
├─ controllers/
│  └─ mainWindowController.py
├─ ui/
│  └─ mainScreen/
│     ├─ mainWindow/
│     ├─ mainWindowPage/
│     └─ heroSection/
└─ viewmodels/
```

---

## Decision tecnica

Se elimina el uso de `presenters/` en favor de un MVC mas explicito:

* la logica de eventos vive en `controllers/`
* la logica de renderizado queda encapsulada en cada vista o subcomponente visual
* `MainWindow` deja de coordinar casos de uso directamente
