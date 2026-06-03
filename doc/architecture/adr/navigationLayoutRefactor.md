# Navigation Layout Refactor

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Decision

La pantalla principal deja de ser una vista unica con todas las secciones apiladas.

La navegacion ahora sigue esta estructura:

```txt
MainWindow
├─ Sidebar fija izquierda
└─ Vista principal derecha
   └─ contenedor de paginas por frames
      ├─ ResumenPage
      ├─ BibliotecaLocalPage
      ├─ PlaylistYouTubePage
      └─ FiltrosPage
```

## Reasoning

El enfoque anterior mezclaba bibliotecas, playlists y filtros en una sola pantalla larga y generaba:

* exceso de cajas y jerarquia visual poco clara
* sensacion de formulario en lugar de aplicacion musical
* peor escalabilidad para futuras vistas como sincronizacion, canciones o artwork

Separar las features en paginas completas mejora foco, navegacion y mantenibilidad sin romper la logica existente.

## UI Criteria

Cada pagina debe:

* ocupar todo el espacio derecho disponible
* usar un header compacto comun
* tener una accion principal clara
* evitar tablas clasicas cuando haya pocos elementos
* usar listas visuales o filas tipo card para contenido guardado

La sidebar queda reservada para navegacion principal y estado minimo contextual.
