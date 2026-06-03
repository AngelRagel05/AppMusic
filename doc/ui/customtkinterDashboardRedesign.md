# CustomTkinter Dashboard Redesign

## Objetivo

Documentar el rediseño completo de AppMusic hacia una interfaz de escritorio moderna basada en `CustomTkinter`.

---

## Decision

La capa de presentacion deja de apoyarse en widgets visuales nativos simples y adopta `CustomTkinter` como base principal para:

* ventana principal
* sidebar
* cards de dashboard
* formularios
* listas visuales
* botones y badges de estado

La razon es visual y estructural:

* mejorar densidad y consistencia
* evitar apariencia de formulario tecnico
* conseguir un dashboard musical de escritorio con tema oscuro real

---

## Componentes clave

La interfaz queda organizada sobre:

* `MainWindow`
* `Sidebar`
* `DashboardView`
* `StatCard`
* `StatusBadge`

Y toda la capa de soporte visual comun vive en:

```txt
app/presentation/uiTheme/
```

---

## Reglas de implementacion

* usar `CTkFrame`, `CTkLabel`, `CTkButton`, `CTkEntry`, `CTkOptionMenu` y `CTkScrollableFrame` siempre que aplique
* evitar `tk.Frame`, `tk.Label`, `tk.Button` y similares en vistas de produccion salvo necesidad tecnica real
* mantener la paleta centralizada en `themePalette.py`
* mantener el layout principal con sidebar fija y area principal a la derecha
* no mostrar estados sueltos fuera de cards, badges o bloques de contexto

---

## Consecuencias

Ventajas:

* mejor apariencia general
* sistema visual mas consistente
* base mas preparada para crecer en nuevas pantallas

Costes:

* nueva dependencia visual en `customtkinter`
* mayor disciplina para no volver a mezclar widgets nativos de forma arbitraria

---

## Evolucion recomendada

Si la aplicacion crece:

* ampliar `uiTheme/` con tokens tipograficos y espaciado
* crear familias de componentes compartidos antes de duplicar vistas
* introducir temas por familia de paginas solo a nivel de tokens, no de implementaciones paralelas
