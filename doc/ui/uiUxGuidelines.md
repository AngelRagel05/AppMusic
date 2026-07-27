# UI/UX Guidelines

## Objetivo

SoundShelf debe sentirse como una herramienta local profesional, oscura y
orientada a productividad. La interfaz presenta tres modulos claramente
separados: Comparacion, Metadata y Descargas.

No debe incorporar reproductor, streaming, portada en reproduccion, volumen,
timeline ni controles de audio.

## Tecnologias

* React y Vite
* JavaScript
* React Router
* TanStack Query
* CSS Modules

No usar Tailwind, Bootstrap ni librerias de componentes.

## Shell

La sidebar global permanece visible en escritorio, puede contraerse y guarda su
estado en `localStorage`. En movil funciona como drawer accesible.

Rutas:

```txt
/comparison
/metadata
/downloads
```

## Lenguaje visual

* fondo oscuro neutro
* superficies elevadas discretas
* verde agua como acento operativo
* rojo solo para error o destruccion
* tipografia de sistema con jerarquia clara
* bordes y sombras contenidos
* animaciones entre 120 y 200 ms

Los tokens globales viven en `frontend/src/styles/global.css`. Los estilos de
cada componente viven en su propio `.module.css` o en el modulo compartido de
UI.

## Componentes

Reutilizar paneles, botones, badges, tablas, estados vacios, barras de progreso
y formularios antes de crear variantes.

Las tablas deben:

* conservar cabeceras y alineacion legibles
* mostrar informacion secundaria con menor contraste
* ofrecer estados vacios explicativos
* permitir navegacion y acciones sin depender solo del color

## Formularios

Cada campo debe tener label. Las acciones primarias describen el efecto real:
por ejemplo `Escribir y verificar tags`, no solo `Guardar`.

La edicion de metadata es individual. No se ofrece edicion masiva hasta que
exista un flujo de confirmacion y rollback adecuado.

## Operaciones largas

La SPA debe permanecer navegable. Mostrar estado, porcentaje, mensaje,
cancelacion y fallo. `cancelling` no se representa como cancelado hasta recibir
confirmacion del backend.

## Accesibilidad

* foco visible
* contraste suficiente
* labels y nombres accesibles
* sidebar movil cerrable con `Escape`
* foco atrapado dentro del drawer abierto
* estados expresados con texto ademas de color
* controles nativos de formulario cuando aporten mejor semantica
