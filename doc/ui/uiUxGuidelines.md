# UI/UX Guidelines

## Objetivo

La aplicacion es un reproductor y gestor musical de escritorio desarrollado con Python, Tkinter y CustomTkinter.

La interfaz debe ser moderna, limpia, oscura, profesional y centrada en la productividad.

Debe inspirarse en aplicaciones como Spotify Desktop, Plexamp, Discord Desktop y Tidal, evitando disenos recargados o excesivamente llamativos.

---

## Tecnologias de UI

* Framework de interfaz: Tkinter con CustomTkinter
* Sistema de estilos: tema centralizado con helpers y factories de `CustomTkinter`
* No utilizar HTML/CSS web
* No utilizar conceptos propios de React, Tailwind o Bootstrap
* Toda la interfaz debe construirse utilizando `CTkFrame`, `CTkLabel`, `CTkButton`, `CTkEntry`, `CTkOptionMenu` y widgets equivalentes cuando sea posible

---

## Sistema de estilos

Los estilos base compartidos deben centralizarse en la capa visual vigente:

```txt
app/presentation/styles/
```

Los widgets deben reutilizar helpers visuales comunes y mantener la paleta compartida.

La estructura minima esperada es:

```txt
app/presentation/styles/
├─ themePalette.py
├─ widgetFactory.py
├─ windowStyler.py
└─ signalSupport.py
```

No se deben dispersar colores, fuentes o reglas de estado fuera de la capa de soporte visual salvo casos excepcionales muy justificados.
Evitar `tk.Label`, `tk.Button`, `tk.Frame` y widgets nativos equivalentes en vistas finales salvo necesidad tecnica concreta.

---

## Paleta de colores

La paleta exacta podra cambiar en el futuro, pero debe respetarse la siguiente filosofia.

### Fondo principal

```txt
#121212
```

### Paneles laterales y secundarios

```txt
#1B1B1B
```

### Superficies elevadas

```txt
#242424
```

### Texto principal

```txt
#FFFFFF
```

### Texto secundario

```txt
#D0D0D0
```

### Texto deshabilitado

```txt
#8A8A8A
```

### Color principal de marca

Rojo oscuro elegante:

```txt
#D64545
```

### Color de acento

Azul grisaceo:

```txt
#5B8DEF
```

---

## Distribucion de color

La interfaz debe respetar aproximadamente:

* 80% colores neutros
* 15% color principal
* 5% color de acento

El color rojo debe destacar acciones importantes.

El azul debe reservarse para estados informativos, indicadores o elementos de apoyo.

---

## Espaciado

Utilizar unicamente multiplos de 8:

```txt
8px
16px
24px
32px
48px
```

Evitar medidas arbitrarias.

---

## Bordes

Todos los componentes deben mantener consistencia:

```txt
Border radius:
8px - 12px
```

No utilizar esquinas completamente cuadradas salvo en tablas o divisores.

---

## Tipografia

Tipografia recomendada:

```txt
Inter
```

Jerarquia visual:

```txt
Titulo principal: 24px
Titulo seccion: 20px
Subtitulo: 16px
Texto normal: 14px
Texto auxiliar: 12px
```

---

## Sidebar

La navegacion principal debe permanecer visible.

Ancho recomendado:

```txt
220px - 260px
```

Secciones sugeridas:

```txt
Inicio
Biblioteca
Favoritos
Playlists
Descargas
Configuracion
```

La sidebar debe sentirse como una columna de navegacion nativa de escritorio:

* fija
* limpia
* con pocas acciones visibles
* sin badges innecesarios ni decoracion excesiva

---

## Navegacion principal

La app debe comportarse como una aplicacion musical de escritorio con navegacion real:

```txt
Sidebar fija izquierda
+ pagina fullscreen a la derecha
```

La vista derecha debe resolverse con paginas separadas dentro de un contenedor de navegacion controlado por frames.

Ejemplo esperado:

* `ResumenPage`
* `BibliotecaLocalPage`
* `PlaylistYouTubePage`
* `FiltrosPage`

No deben convivir todas las features principales apiladas en la misma pantalla.

## Paginas de contenido

Cada pagina debe seguir este patron:

* header compacto con titulo, contexto activo y acciones principales
* un bloque principal claro, sin cadenas de cards anidadas
* contenido centrado en musica, playlists, filtros o sincronizacion segun la vista
* feedback contextual dentro de su propia pagina

Cuando haya pocos elementos, priorizar:

* listas visuales
* filas tipo card
* estados vacios bien resueltos

Evitar por defecto:

* tablas grandes para colecciones pequenas
* cards dentro de cards sin una razon clara
* formularios largos cuando solo hay uno o dos campos

La estetica debe inspirarse mas en Spotify, Apple Music, Plex o Notion que en un dashboard corporativo.

---

## Reproductor

Debe existir una barra de reproduccion persistente en la parte inferior.

Estructura:

```txt
Portada
Titulo
Artista

Anterior
Play/Pause
Siguiente

Barra de progreso

Control de volumen
```

Altura aproximada:

```txt
80px - 90px
```

---

## Tablas de canciones

Las tablas deben priorizar la legibilidad.

Columnas recomendadas:

```txt
Portada
Titulo
Artista
Album
Duracion
Fecha de anadido
```

Evitar sobrecargar las filas con informacion innecesaria.

---

## Botones

### Boton primario

Usar para:

* Descargar
* Guardar
* Crear playlist
* Confirmar

Debe utilizar el color principal de marca.

### Boton secundario

Usar para:

* Editar
* Buscar
* Actualizar
* Navegar

Debe utilizar colores neutros.

### Boton destructivo

Usar unicamente para:

* Eliminar
* Borrar
* Restablecer

Debe diferenciarse claramente del resto.

---

## Animaciones

Las animaciones deben ser minimas.

Duracion estandar:

```txt
200ms
```

Objetivos:

* Hover
* Focus
* Apertura de paneles

Evitar animaciones complejas o excesivas.

---

## Componentes reutilizables

Antes de crear un nuevo componente:

1. Buscar uno existente.
2. Extender el componente existente si es posible.
3. Crear uno nuevo unicamente cuando sea necesario.

La consistencia visual tiene prioridad sobre la personalizacion.

---

## Identificadores visuales

Cuando haga falta diferenciar widgets reutilizables, encapsular esa decision en componentes o helpers de estilo en vez de depender de jerarquias fragiles.

---

## Accesibilidad

* Mantener contraste alto
* El texto siempre debe ser legible
* Los estados `hover` y `selected` deben ser claramente visibles
* No depender exclusivamente del color para transmitir informacion

---

## Reglas para IA y futuros desarrolladores

* Mantener siempre una estetica oscura y profesional
* Priorizar funcionalidad sobre decoracion
* Mantener consistencia visual en todas las ventanas
* Reutilizar componentes existentes
* Centralizar estilos y helpers visuales en la capa compartida de CustomTkinter
* No introducir frameworks web
* No introducir CSS web
* No mezclar paradigmas de React con Tkinter ni mezclar widgets nativos y CTk sin necesidad real
* Todo nuevo componente debe respetar estas directrices
* La experiencia de usuario debe sentirse como una aplicacion de escritorio profesional, no como una pagina web empaquetada
