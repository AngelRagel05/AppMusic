# Tkinter Migration

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Objetivo

Documentar la migracion completa de la capa de interfaz al stack actual basado en `Tkinter`.

---

## Motivo

Se adopta `Tkinter` para reducir dependencias externas en la interfaz y simplificar el arranque nativo de escritorio.

---

## Alcance

La migracion afecta a:

* `app/main.py`
* `app/presentation/controllers/mainWindowController.py`
* `app/presentation/ui/`
* `app/presentation/styles/`
* dependencias declaradas en `pyproject.toml` y `requirements.txt`

No cambia:

* `application/`
* `domain/`
* `infrastructure/`
* contratos de `viewmodels`

---

## Decision tecnica

La nueva capa UI mantiene la misma responsabilidad arquitectonica:

* la ventana principal crea y muestra la aplicacion
* `AppLayout` coordina navegacion
* los controladores orquestan eventos y casos de uso
* las vistas solo leen y renderizan estado

Para no contaminar el resto del sistema con detalles de `Tkinter`, se introducen adaptadores pequenos en `app/presentation/uiTheme/`:

* `themePalette.py`
* `widgetFactory.py`
* `windowStyler.py`
* `signalSupport.py`

Con esto se preserva una API de presentacion estable para los controladores aunque cambie el toolkit.

---

## Consecuencias

Ventajas:

* menos dependencias de GUI
* arranque mas simple
* menor acoplamiento a APIs especificas del toolkit anterior

Costes:

* se deja de usar hojas de estilo Qt
* algunos patrones visuales se resuelven ahora con composicion manual de widgets `Tkinter`
* la guia UI del proyecto queda alineada con `Tkinter`

---

## Seguimiento recomendado

Pendientes razonables despues de la migracion:

* introducir pruebas de humo para arranque de la UI
* mantener futuros componentes sobre `uiTheme/` y la paleta compartida
* unificar futuros componentes sobre `getPageTheme(...)` y factories compartidos
