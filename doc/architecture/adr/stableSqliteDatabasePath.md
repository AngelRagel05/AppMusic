# ADR: ruta estable para la base de datos SQLite

## Estado

Aceptada

## Contexto

La aplicacion estaba configurada con `DATABASE_URL=sqlite:///music_app.db`.

En SQLite, esa URL usa una ruta relativa al directorio actual del proceso.

Eso provoca que, si la app se lanza desde ubicaciones distintas, termine abriendo o creando bases de datos diferentes.

El efecto visible para el usuario es:

* comparaciones aparentemente no guardadas
* historico inconsistente entre sesiones
* bibliotecas o playlists activas que parecen cambiar o desaparecer segun desde donde se arranque la app

## Decision

Resolver automaticamente las rutas SQLite relativas contra la raiz del proyecto antes de crear la sesion de SQLAlchemy.

Reglas:

* si `DATABASE_URL` es SQLite y ya apunta a una ruta absoluta, no se modifica
* si `DATABASE_URL` es SQLite y usa una ruta relativa, se convierte en absoluta respecto a la raiz del proyecto
* si la URL no es SQLite, se deja intacta

## Consecuencias

Positivas:

* la app usa siempre el mismo archivo `music_app.db`
* las comparaciones persistidas y el historico sobreviven a reinicios y cambios de directorio de arranque
* se reduce el riesgo de diagnosticos falsos sobre perdida de datos

Consideraciones:

* si existian bases de datos creadas en otros directorios por ejecuciones previas, esos datos no se migran automaticamente
* a partir de esta decision, la ubicacion efectiva por defecto queda anclada a la raiz del proyecto
