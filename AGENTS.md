# AGENTS.md

## Objetivo de este archivo

Este archivo define como deben trabajar las IA dentro del proyecto.

Aqui no debe vivir la documentacion funcional o tecnica extensa del producto.

Para eso existe la carpeta `doc/`.

Si hay conflicto entre un resumen previo y este archivo, prevalece `AGENTS.md`.

---

## Rol de la IA

La IA debe actuar como asistente tecnico de desarrollo.

Debe:

* Respetar la arquitectura del proyecto.
* Mantener codigo claro y facil de extender.
* Aplicar principios SOLID cuando tenga sentido.
* Evitar sobreingenieria.
* Proponer cambios pequenos, coherentes y verificables.

### Permiso para lectura de archivos

El usuario autoriza a la IA a ejecutar comandos de lectura de archivos y exploracion del arbol del proyecto cuando sean necesarios para analizar, revisar o modificar el codigo.

Esto incluye, por ejemplo:

* lectura de archivos de codigo, configuracion y documentacion
* busquedas de texto en el proyecto
* listado de carpetas y archivos
* inspeccion de estructura dentro de `app/`, `tests/`, `doc/` y rutas relacionadas

Este permiso aplica como regla general de trabajo dentro del repositorio.

---

## Reglas de diseño

### SOLID

Aplicar SOLID como criterio general:

* Single Responsibility Principle
* Open/Closed Principle
* Liskov Substitution Principle
* Interface Segregation Principle
* Dependency Inversion Principle

No usar SOLID como excusa para crear capas o abstracciones innecesarias.

---

## Arquitectura base

El proyecto sigue una arquitectura limpia ligera con separacion por responsabilidades.

Estructura base:

```txt
app/
├─ main.py
├─ presentation/
├─ application/
├─ domain/
├─ infrastructure/
├─ workers/
├─ config/
└─ utils/

tests/
migrations/
doc/
```

### Regla principal

Cada vez que se añada algo nuevo, preguntarse:

```txt
¿Es UI?
→ presentation

¿Es una accion del usuario o del sistema?
→ application/use_cases

¿Es una regla de negocio pura?
→ domain

¿Toca base de datos, filesystem, red, ffmpeg, Mutagen, yt-dlp o APIs externas?
→ infrastructure

¿Puede bloquear la interfaz?
→ workers
```

---

## Responsabilidades por capa

### presentation

Contiene interfaz, widgets, ventanas, tablas, formularios y viewmodels.

No debe:

* Acceder directamente a base de datos
* Ejecutar herramientas externas
* Contener logica de negocio pesada

### application

Contiene use cases y DTOs.

Cada use case representa una accion clara del sistema y debe tener un metodo principal:

```python
execute(...)
```

### domain

Contiene entidades, value objects y servicios de dominio.

No debe depender de frameworks de UI, ORM ni infraestructura.

### infrastructure

Contiene implementaciones concretas para base de datos, archivos, red, metadata, audio y servicios externos.

### workers

Contiene tareas en segundo plano para evitar bloquear la UI.

Los workers emiten senales o resultados. No actualizan widgets directamente desde hilos secundarios.

---

## Convenciones de nombres

### snake_case

Usar `snake_case` en:

* nombres de tablas de base de datos

Ejemplos:

```txt
youtube_playlist
local_song
playlist_comparison_result
```

### PascalCase

Usar `PascalCase` en:

* clases
* widgets
* entidades
* use cases

Ejemplos:

```txt
MainWindow
ScanMusicFolderUseCase
SongRepository
```

### camelCase

Usar `camelCase` en:

* nombres de archivos
* funciones
* variables
* carpetas

Si una libreria externa obliga a otra nomenclatura, respetar el formato externo solo en la capa de adaptacion.

Ejemplos:

```txt
scanMusicFolder.py
editSongMetadata.py
downloadSong
songTitle
```

### PascalCase

Usar `PascalCase` en:

* clases
* widgets
* entidades
* use cases

Ejemplos:

```txt
MainWindow
ScanMusicFolderUseCase
SongRepository
```

### UPPER_SNAKE_CASE

Usar `UPPER_SNAKE_CASE` para constantes.

### Reglas adicionales de nomenclatura

La IA debe mantener esta nomenclatura de forma consistente en:

* nombres de tablas
* nombres de tablas intermedias
* nombres de columnas si se documentan
* nombres de archivos
* nombres de carpetas
* nombres de funciones
* nombres de variables
* nombres de clases
* nombres de DTOs
* nombres de use cases
* nombres documentados en `doc/bbdd/`

### kebab-case

Usar `kebab-case` solo cuando aplique fuera de Python, por ejemplo:

* nombres de assets web
* identificadores de build
* nombres de paquetes o artefactos
* nombres de workflows o scripts del sistema si encaja mejor

No usar `kebab-case` para modulos Python.

---

## Reglas de implementacion

### UI

La UI no hace trabajo pesado.

Incorrecto:

```txt
boton
→ escanea carpeta
→ lee archivos
→ guarda en base de datos
```

Correcto:

```txt
boton
→ lanza worker
→ worker ejecuta use case
→ use case coordina servicios
```

### UI y UX

La interfaz debe sentirse como una aplicacion de escritorio profesional, no como una web empaquetada.

Reglas operativas:

* Usar Tkinter y sus widgets nativos como base de interfaz
* Centralizar tema, colores y helpers visuales en una capa compartida de presentacion
* Evitar estilos dispersos dentro de ventanas o widgets salvo excepciones justificadas
* Mantener una estetica oscura, limpia y orientada a productividad
* Reutilizar componentes visuales antes de crear otros nuevos
* No introducir HTML/CSS web ni paradigmas de React, Tailwind o Bootstrap
* Respetar espaciados consistentes y una jerarquia tipografica clara
* Mantener sidebar, paneles, tablas y barras persistentes con estructura entendible para usuario final
* Todo componente visual dentro de `app/presentation/ui/` debe vivir en su propia carpeta con su modulo principal y, si hace falta, helpers locales estrictamente visuales
* Cuando varios componentes formen parte de una misma pantalla o feature, deben agruparse dentro de una carpeta padre con nombre de feature, no reutilizar el nombre de uno de sus hijos
* Los helpers no visuales no deben vivir dentro de `app/presentation/ui/`; deben ir fuera de UI dentro de `presentation` segun su responsabilidad

La guia completa de UI/UX debe mantenerse en `doc/ui/ui_ux_guidelines.md`.

### Repositories

Los repositories deben ocultar el ORM o la tecnologia de persistencia.

La UI y los use cases no deben escribir consultas SQL manuales.

### Infraestructura externa

Toda integracion con herramientas externas debe quedar aislada en `infrastructure`.

Ejemplos:

* `yt-dlp`
* `ffmpeg`
* `Mutagen`
* `httpx`
* SQLite o MySQL mediante SQLAlchemy

### Base de datos

La base de datos guarda indice, estado y relaciones de la app.

El archivo MP3 sigue siendo la fuente real de metadata musical.

### Caratulas

Las caratulas deben vivir embebidas en el MP3.

No guardar caratulas en la base de datos.

---

## Testing

Probar especialmente:

* use cases
* servicios de dominio
* repositories
* validaciones importantes

Los tests deben ser claros y centrados en comportamiento.

Nombrado:

```txt
test_nombre_del_comportamiento.py
```

---

## Configuracion

Toda ruta o valor configurable debe salir de `.env` o de configuracion persistida.

No hardcodear rutas absolutas personales.

---

## Documentacion

`AGENTS.md` es solo para reglas de trabajo de las IA.

La documentacion tecnica del proyecto debe ir en `doc/`.

Ejemplos:

* arquitectura
* diseno de base de datos
* roadmap tecnico
* decisiones de integracion
* flujos funcionales

### Reglas para documentacion de BBDD

Toda la documentacion de base de datos debe vivir dentro de `doc/bbdd/`.

La IA debe mantener al menos estos documentos cuando se disene o cambie la base de datos:

* `er_model.md`
* `relational_model.md`
* `tables/` para detalle de tablas si el proyecto crece

El contenido esperado es:

* `er_model.md`
  * modelo entidad-relacion conceptual
  * entidades
  * relaciones
  * cardinalidades
  * restricciones o notas de negocio relevantes
* `relational_model.md`
  * modelo relacional completo
  * tablas
  * columnas
  * claves primarias
  * claves foraneas
  * unicidad
  * nulabilidad
  * relaciones entre tablas

Regla visual para el modelo entidad-relacion:

* Debe seguir estilo conceptual clasico
* Debe mostrar entidades, relaciones y cardinalidades
* Debe representarse como el ejemplo de referencia dado por el usuario
* Las cardinalidades deben verse de forma explicita como `(0,1)`, `(1,1)`, `(0,n)` o `(1,n)` cuando aplique
* Debe escribirse en Markdown usando bloques `mermaid`

Regla visual para el modelo relacional:

* Debe mostrar la tabla completa
* Debe incluir sus atributos
* Debe marcar PK y FK
* Debe reflejar claramente las relaciones entre tablas
* Debe escribirse en Markdown usando bloques `mermaid`

Regla de detalle por tabla:

* Cuando se documente una tabla concreta dentro de `doc/bbdd/tables/`, el archivo debe ser `.md`
* Debe incluir descripcion funcional de la tabla
* Debe incluir columnas y restricciones relevantes
* Si aplica, debe incluir un diagrama `mermaid` relacionado con sus dependencias

Antes de crear migraciones o modelos ORM nuevos, la IA debe intentar dejar actualizada la documentacion de `doc/bbdd/`.
