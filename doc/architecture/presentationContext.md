# Contexto de Presentacion

## Objetivo

La presentacion de SoundShelf es una SPA React servida por Vite durante el
desarrollo y por FastAPI desde su build estatico en produccion. Electron aporta
la ventana nativa, el arranque y el cierre de procesos; no sustituye ni duplica
la presentacion React. No existe una capa Tkinter.

## Estructura

```txt
frontend/src/
├─ app/
├─ features/
│  ├─ comparison/
│  ├─ metadata/
│  └─ downloads/
├─ shared/
│  ├─ api/
│  ├─ components/
│  ├─ hooks/
│  └─ styles/
└─ styles/
```

La navegacion global usa React Router. TanStack Query gestiona datos remotos,
invalidaciones y polling. Las llamadas HTTP se centralizan en
`shared/api/apiClient.js`.

El cliente HTTP obtiene `apiBaseUrl` de la URL inicial proporcionada por
Electron. El valor solo se acepta si usa HTTP y apunta al loopback local. Sin
ese parametro se conserva la ruta relativa `/api`, util para ejecutar la SPA
directamente con Vite.

La ventana de escritorio mantiene marco nativo, recuerda tamaño y posicion y
no expone Node.js al renderer. La navegacion fuera del origen local se bloquea;
los enlaces HTTP externos se abren con el navegador del sistema.

## Shell global

La sidebar izquierda enlaza las tres herramientas y persiste su estado
contraido en `localStorage`. En pantallas estrechas se convierte en drawer con
cierre por `Escape`, bloqueo de foco y backdrop.

No existe barra de reproduccion ni controles multimedia.

## Estado y feedback

Las operaciones largas devuelven una tarea y la SPA consulta `/api/tasks`
periodicamente. Cada modulo muestra progreso, cancelacion, errores y reintentos
sin bloquear la navegacion.

Los modulos se enlazan mediante identificadores persistidos. Comparacion abre
`/downloads?comparisonId=<id>` y Descargas vuelve a consultar el snapshot para
mostrar y seleccionar los items faltantes; no comparte objetos mediante estado
global de React.

Los errores de API usan el contrato:

```json
{
  "error": {
    "code": "business_rule_violation",
    "message": "Descripcion legible",
    "details": null
  }
}
```

## Estilos

Se usan CSS Modules, tokens CSS compartidos y componentes propios. No se usan
frameworks visuales, Tailwind ni Bootstrap.
