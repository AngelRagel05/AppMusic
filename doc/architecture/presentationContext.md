# Contexto de Presentacion

## Objetivo

La presentacion de SoundShelf es una SPA React servida por Vite durante el
desarrollo. No existe una capa Tkinter ni un runtime de escritorio empaquetado.

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
