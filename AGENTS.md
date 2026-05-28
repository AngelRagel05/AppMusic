# AGENTS.md

## Objetivo del proyecto

Este proyecto es una aplicación de escritorio en Python para gestionar, reproducir y organizar música local.

La aplicación mezcla ideas de:

* VLC: reproducción de música local.
* Mp3Tag: edición de metadatos.
* Descargador musical: descarga de audio desde URLs compatibles.
* Sincronizador de playlists: comparación entre playlists de YouTube y canciones locales.

La app debe permitir:

* Escanear una carpeta local de música.
* Detectar archivos MP3.
* Leer metadatos.
* Reproducir canciones.
* Editar título, artista, álbum, año, número de pista y carátula.
* Descargar audio desde YouTube.
* Leer playlists de YouTube.
* Detectar qué canciones de una playlist faltan en local.
* Guardar información en una base de datos local SQLite.
* Mantener una arquitectura limpia y escalable.

---

## Stack tecnológico

### Python 3.12

Lenguaje principal de la aplicación.

Se debe usar sintaxis moderna de Python, tipado cuando tenga sentido y código claro.

---

### PySide6

Framework para crear la interfaz gráfica de escritorio.

Equivale mentalmente a la capa visual de una app web, como React, Vue o Blade en Laravel.

Se usa para:

* Ventanas.
* Botones.
* Tablas.
* Formularios.
* Barra de reproducción.
* Eventos de usuario.
* Reproductor usando Qt Multimedia.

La UI no debe contener lógica pesada.

---

### SQLAlchemy

ORM para trabajar con la base de datos usando objetos Python.

Equivale aproximadamente a Eloquent en Laravel.

Se usa para:

* Definir modelos persistentes.
* Consultar canciones.
* Guardar playlists.
* Actualizar metadatos.
* Evitar SQL manual repartido por toda la app.

---

### Alembic

Sistema de migraciones para SQLAlchemy.

Equivale a las migrations de Laravel.

Se usa para:

* Crear tablas.
* Modificar columnas.
* Versionar cambios de base de datos.
* Mantener la estructura de SQLite controlada.

---

### SQLite

Base de datos local de la aplicación.

Es suficiente para miles de canciones y evita tener que instalar MySQL o PostgreSQL.

Se usa para guardar:

* Canciones escaneadas.
* Rutas de archivos.
* Playlists.
* Items de playlist.
* Estado de descargas.
* Configuración de la app.
* Historial o favoritos si se añaden después.

---

### yt-dlp

Herramienta para descargar audio y obtener información de YouTube/playlists.

Se usa para:

* Descargar canciones.
* Extraer información de vídeos.
* Leer playlists.
* Obtener títulos, duración y miniaturas.

La app debe usar esta herramienta solo con contenido que el usuario tenga derecho a descargar.

---

### ffmpeg

Herramienta multimedia externa.

Se usa para:

* Convertir audio.
* Extraer MP3.
* Procesar bitrate.
* Normalizar formatos.
* Ayudar a yt-dlp en la conversión final.

---

### Mutagen

Librería para leer y editar metadatos de archivos de audio.

Se usa para:

* Leer título.
* Leer artista.
* Leer álbum.
* Leer año.
* Leer número de pista.
* Leer duración.
* Leer carátula embebida.
* Escribir metadatos ID3 en MP3.
* Cambiar la portada del archivo.

La carátula debe vivir dentro del MP3 como metadato embebido.

No guardar imágenes en la base de datos.

No usar Cloudinary.

No crear caché permanente de carátulas al principio salvo que sea estrictamente necesario por rendimiento.

---

### Pillow

Librería para manipular imágenes.

Se usa solo cuando haga falta:

* Redimensionar carátulas.
* Convertir formatos de imagen.
* Validar imágenes antes de incrustarlas en el MP3.

No debe usarse para crear una caché permanente de portadas salvo decisión explícita futura.

---

### httpx

Cliente HTTP moderno.

Se usa para:

* Peticiones a APIs.
* Descargar recursos externos si hace falta.
* Consultas auxiliares relacionadas con playlists o metadatos.

---

### python-dotenv

Carga configuración desde archivos `.env`.

Se usa para configurar:

* Carpeta de música.
* Carpeta de descargas.
* Ruta de ffmpeg.
* Ruta de base de datos.
* Configuración de logs.

---

### loguru

Sistema de logs simple y potente.

Se usa para:

* Registrar errores.
* Registrar descargas.
* Registrar escaneos.
* Registrar problemas de metadatos.
* Depurar fallos de ffmpeg, yt-dlp o base de datos.

---

### PyInstaller

Herramienta para generar el `.exe` final de la app.

Se usa al final del desarrollo para empaquetar la aplicación como programa de escritorio.

No es necesario usarlo durante el desarrollo diario.

---

### ruff

Linter y formateador de código Python.

Se usa para mantener el código limpio, ordenado y consistente.

---

### pytest

Framework de tests.

Se usa para probar:

* Use cases.
* Servicios de dominio.
* Repositories.
* Normalización de nombres.
* Comparación entre canciones locales y canciones de YouTube.

---

## Arquitectura general

El proyecto sigue una arquitectura DDD ligera / hexagonal.

No se debe hacer DDD enterprise complejo.

No usar:

* CQRS.
* Event sourcing.
* Domain events complejos.
* Bounded contexts innecesarios.
* Capas excesivas.

Sí usar:

* Entities.
* Value Objects.
* Use Cases.
* Repositories.
* Services.
* Infrastructure separada.
* Presentation separada.

---

## Comparación mental con Laravel

Esta app no usa Laravel, pero la estructura puede entenderse así:

```txt
Laravel Controller
≈ PySide6 View / ViewModel

Laravel Action / Service
≈ Application Use Case

Laravel Eloquent Model
≈ SQLAlchemy Model

Laravel Migration
≈ Alembic Migration

Laravel Job
≈ Worker de PySide6 / QThread

Laravel Storage / HTTP / DB
≈ Infrastructure

Laravel Request / DTO
≈ Application DTO

Laravel config()
≈ config/settings.py + .env
```

Flujo típico en Laravel:

```txt
Controller
↓
Service / Action
↓
Repository / Model
↓
Database
```

Flujo típico en esta app:

```txt
Presentation UI
↓
Application Use Case
↓
Domain / Services
↓
Infrastructure Repository
↓
SQLite / Filesystem / yt-dlp / Mutagen
```

---

## Estructura recomendada

```txt
music_app/
├─ app/
│  ├─ main.py
│  │
│  ├─ presentation/
│  │  ├─ ui/
│  │  └─ viewmodels/
│  │
│  ├─ application/
│  │  ├─ use_cases/
│  │  └─ dto/
│  │
│  ├─ domain/
│  │  ├─ entities/
│  │  ├─ value_objects/
│  │  └─ services/
│  │
│  ├─ infrastructure/
│  │  ├─ database/
│  │  ├─ repositories/
│  │  ├─ youtube/
│  │  ├─ filesystem/
│  │  ├─ metadata/
│  │  └─ audio/
│  │
│  ├─ workers/
│  │
│  ├─ config/
│  │
│  └─ utils/
│
├─ migrations/
├─ tests/
├─ .env
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

---

## Responsabilidad de cada carpeta

### app/main.py

Punto de entrada de la aplicación.

Debe:

* Crear la app de PySide6.
* Cargar configuración.
* Inicializar logging.
* Inicializar dependencias principales.
* Abrir la ventana principal.

No debe contener lógica de negocio.

---

### app/presentation/

Capa visual.

Equivale a la parte de React/Vue/Blade en una app Laravel.

Contiene:

* Ventanas.
* Componentes visuales.
* Tablas.
* Formularios.
* ViewModels.
* Eventos de botones.
* Renderizado de datos.

No debe:

* Hablar directamente con SQLAlchemy.
* Llamar directamente a Mutagen.
* Ejecutar yt-dlp directamente.
* Contener reglas de negocio importantes.

La UI debe llamar a Use Cases.

---

### app/presentation/ui/

Componentes visuales concretos.

Ejemplos:

```txt
main_window.py
library_view.py
player_bar.py
download_view.py
metadata_editor.py
playlist_sync_view.py
settings_view.py
```

---

### app/presentation/viewmodels/

Estado y adaptación de datos para la UI.

Sirve para evitar que la UI dependa directamente de entidades internas.

Ejemplos:

```txt
song_table_viewmodel.py
download_queue_viewmodel.py
player_viewmodel.py
```

---

### app/application/

Capa de aplicación.

Aquí viven los casos de uso.

Equivale a `app/Actions` o `app/Services` en Laravel.

No debe depender de PySide6.

Debe coordinar acciones del sistema.

---

### app/application/use_cases/

Cada archivo representa una acción importante del usuario o del sistema.

Ejemplos:

```txt
scan_music_folder.py
play_song.py
pause_song.py
download_song.py
edit_song_metadata.py
sync_youtube_playlist.py
delete_song.py
refresh_song_metadata.py
search_library.py
```

Regla:

```txt
1 Use Case = 1 acción clara del sistema
```

Ejemplo:

* `ScanMusicFolderUseCase`
* `DownloadSongUseCase`
* `EditSongMetadataUseCase`
* `SyncYoutubePlaylistUseCase`

Un Use Case puede usar:

* Repositories.
* Domain services.
* Infrastructure services mediante interfaces.
* DTOs.

Un Use Case no debe saber detalles visuales de PySide6.

---

### app/application/dto/

Objetos simples para transportar datos.

Equivale a Data Objects en Laravel.

Ejemplos:

```txt
song_dto.py
download_request_dto.py
metadata_update_dto.py
playlist_item_dto.py
```

Se usan para pasar datos entre UI, Use Cases e Infrastructure sin acoplar todo.

---

### app/domain/

Capa de dominio.

Aquí vive la lógica pura del negocio.

No debe depender de:

* PySide6.
* SQLAlchemy.
* yt-dlp.
* ffmpeg.
* Mutagen.
* SQLite.
* httpx.

Debe poder probarse sin abrir la app ni tocar archivos reales.

---

### app/domain/entities/

Entidades principales del negocio.

Ejemplos:

```txt
song.py
playlist.py
playlist_item.py
download.py
```

Una entidad representa conceptos importantes.

Ejemplo `Song`:

* id
* path
* title
* artist
* album
* year
* track_number
* duration

---

### app/domain/value_objects/

Objetos de valor.

Representan valores importantes con validación.

Ejemplos:

```txt
song_path.py
youtube_url.py
metadata.py
duration.py
track_number.py
```

Ejemplo:

`YoutubeUrl` debería validar que la URL tiene formato aceptable antes de intentar descargar.

---

### app/domain/services/

Servicios de dominio.

Contienen reglas puras que no pertenecen claramente a una entidad.

Ejemplos:

```txt
song_matcher.py
metadata_validator.py
filename_normalizer.py
```

Ejemplo:

`SongMatcher` compara una canción local con un vídeo de YouTube para decidir si probablemente son la misma canción.

---

### app/infrastructure/

Capa de infraestructura.

Aquí vive todo lo que toca el mundo exterior.

Equivale a:

* DB.
* Storage.
* HTTP clients.
* External services.
* Drivers.
* CLI tools.

Esta capa sí puede usar:

* SQLAlchemy.
* SQLite.
* yt-dlp.
* ffmpeg.
* Mutagen.
* httpx.
* filesystem.

---

### app/infrastructure/database/

Configuración de base de datos.

Ejemplos:

```txt
base.py
session.py
engine.py
models.py
```

Aquí van:

* Declarative Base.
* Engine.
* SessionLocal.
* Modelos SQLAlchemy si se decide separarlos de las entidades de dominio.

Recomendación:

Mantener separados los modelos SQLAlchemy de las entidades de dominio si el proyecto crece.

Para empezar, se puede aceptar una separación simple, pero no meter lógica de negocio en modelos SQLAlchemy.

---

### app/infrastructure/repositories/

Implementaciones concretas de repositorios.

Ejemplos:

```txt
sqlalchemy_song_repository.py
sqlalchemy_playlist_repository.py
sqlalchemy_settings_repository.py
```

Equivale a encapsular consultas Eloquent.

La UI no debe hacer queries directas.

Los Use Cases deben llamar a repositorios.

---

### app/infrastructure/youtube/

Integración con YouTube usando yt-dlp.

Ejemplos:

```txt
ytdlp_downloader.py
ytdlp_playlist_reader.py
youtube_video_info.py
```

Aquí debe estar toda la lógica relacionada con yt-dlp.

No mezclar yt-dlp dentro de Use Cases ni UI.

---

### app/infrastructure/filesystem/

Acceso a archivos y carpetas.

Ejemplos:

```txt
music_folder_scanner.py
file_locator.py
safe_filename.py
```

Responsabilidades:

* Buscar archivos MP3.
* Validar rutas.
* Crear nombres seguros.
* Detectar archivos duplicados.
* Comprobar existencia de carpetas.

---

### app/infrastructure/metadata/

Lectura y escritura de metadatos usando Mutagen y Pillow.

Ejemplos:

```txt
mutagen_metadata_reader.py
mutagen_metadata_writer.py
cover_image_processor.py
```

Responsabilidades:

* Leer tags.
* Escribir tags.
* Leer carátula embebida.
* Cambiar carátula.
* Validar imágenes.
* Convertir imagen si hace falta.

---

### app/infrastructure/audio/

Reproducción y control de audio.

Ejemplos:

```txt
qt_audio_player.py
playback_queue.py
```

Responsabilidades:

* Play.
* Pause.
* Stop.
* Next.
* Previous.
* Volume.
* Seek.
* Estado de reproducción.

---

### app/workers/

Tareas en segundo plano.

Equivale a Jobs de Laravel.

Se usan para evitar que la UI se congele.

Ejemplos:

```txt
scan_worker.py
download_worker.py
playlist_sync_worker.py
metadata_update_worker.py
```

Deben usarse para:

* Escaneo de carpetas.
* Descargas.
* Conversión.
* Sincronización de playlists.
* Operaciones pesadas de metadatos.

---

### app/config/

Configuración central de la app.

Ejemplos:

```txt
settings.py
paths.py
```

Debe leer variables desde `.env`.

Ejemplo de `.env`:

```env
APP_NAME=MusicApp
DATABASE_URL=sqlite:///./music_app.sqlite3
MUSIC_FOLDER=D:/Music
DOWNLOAD_FOLDER=D:/Music
FFMPEG_PATH=ffmpeg
LOG_LEVEL=INFO
```

---

### app/utils/

Funciones auxiliares genéricas.

Ejemplos:

```txt
logger.py
string_utils.py
time_utils.py
file_utils.py
```

No debe convertirse en un cajón desastre.

Si una utilidad empieza a tener lógica de negocio, moverla a `domain/services`.

---

### migrations/

Migraciones de Alembic.

Equivale a `database/migrations` en Laravel.

Cada cambio estructural de base de datos debe ir con migración.

---

### tests/

Tests automáticos.

Estructura sugerida:

```txt
tests/
├─ unit/
│  ├─ domain/
│  └─ application/
│
├─ integration/
│  ├─ repositories/
│  ├─ metadata/
│  └─ youtube/
│
└─ conftest.py
```

---

## Reglas importantes de arquitectura

### 1. La UI no hace trabajo pesado

Incorrecto:

```txt
button_clicked()
→ escanea carpeta
→ lee MP3
→ guarda en DB
```

Correcto:

```txt
button_clicked()
→ lanza ScanWorker
→ worker llama a ScanMusicFolderUseCase
→ use case coordina servicios
```

---

### 2. La UI no accede directamente a la base de datos

Incorrecto:

```txt
library_view.py usa SQLAlchemy directamente
```

Correcto:

```txt
library_view.py
→ SearchLibraryUseCase
→ SongRepository
→ SQLite
```

---

### 3. Los Use Cases no deben depender de PySide6

Incorrecto:

```txt
DownloadSongUseCase importa QWidget
```

Correcto:

```txt
DownloadSongUseCase no sabe nada de ventanas
```

---

### 4. El dominio no depende de infraestructura

Incorrecto:

```txt
domain/song.py importa mutagen
```

Correcto:

```txt
infrastructure/metadata/mutagen_metadata_reader.py usa mutagen
```

---

### 5. yt-dlp debe estar aislado

Incorrecto:

```txt
download_view.py ejecuta yt-dlp
```

Correcto:

```txt
download_view.py
→ DownloadSongUseCase
→ YtdlpDownloader
```

---

### 6. Mutagen debe estar aislado

Incorrecto:

```txt
metadata_editor.py escribe tags directamente con Mutagen
```

Correcto:

```txt
metadata_editor.py
→ EditSongMetadataUseCase
→ MutagenMetadataWriter
```

---

### 7. ffmpeg debe estar aislado

Toda llamada a ffmpeg debe vivir en infraestructura.

---

### 8. La base de datos no es la fuente absoluta de metadata

La fuente real de los metadatos musicales es el archivo MP3.

SQLite guarda una copia/index para buscar rápido.

Cuando se edita metadata:

```txt
1. Se escribe en el MP3 con Mutagen.
2. Se actualiza SQLite.
```

---

### 9. Las carátulas viven dentro del MP3

No guardar carátulas en SQLite.

No usar Cloudinary.

No crear caché permanente al principio.

Si en el futuro hay problemas de rendimiento, se podrá añadir caché opcional.

---

## Cómo añadir una nueva funcionalidad

Para añadir una funcionalidad nueva, seguir este orden.

Ejemplo: añadir favoritos.

### 1. Definir la acción

```txt
El usuario puede marcar una canción como favorita.
```

### 2. Crear o modificar entidad de dominio

```txt
domain/entities/song.py
```

Añadir campo conceptual:

```txt
is_favorite
```

### 3. Crear migración

Añadir columna en SQLite mediante Alembic:

```txt
songs.is_favorite
```

### 4. Actualizar repository

```txt
infrastructure/repositories/sqlalchemy_song_repository.py
```

Añadir método:

```txt
mark_as_favorite(song_id)
unmark_as_favorite(song_id)
```

### 5. Crear Use Case

```txt
application/use_cases/mark_song_as_favorite.py
```

### 6. Actualizar UI

```txt
presentation/ui/library_view.py
```

Añadir botón o acción visual.

### 7. Añadir tests

```txt
tests/unit/application/test_mark_song_as_favorite.py
```

---

## Ejemplo de flujo completo: editar metadata

```txt
Usuario edita título/artista/álbum en metadata_editor.py
↓
UI crea MetadataUpdateDTO
↓
EditSongMetadataUseCase.execute(dto)
↓
MetadataValidator valida datos
↓
MutagenMetadataWriter escribe en el MP3
↓
SongRepository actualiza SQLite
↓
UI refresca la tabla
```

Archivos implicados:

```txt
presentation/ui/metadata_editor.py
application/dto/metadata_update_dto.py
application/use_cases/edit_song_metadata.py
domain/services/metadata_validator.py
infrastructure/metadata/mutagen_metadata_writer.py
infrastructure/repositories/sqlalchemy_song_repository.py
```

---

## Ejemplo de flujo completo: descargar canción

```txt
Usuario pega URL en download_view.py
↓
DownloadWorker evita congelar UI
↓
DownloadSongUseCase.execute(url)
↓
YoutubeUrl valida URL
↓
YtdlpDownloader descarga audio
↓
ffmpeg convierte a MP3 si hace falta
↓
MutagenMetadataWriter escribe metadata inicial
↓
SongRepository guarda canción en SQLite
↓
UI muestra la canción descargada
```

Archivos implicados:

```txt
presentation/ui/download_view.py
workers/download_worker.py
application/use_cases/download_song.py
domain/value_objects/youtube_url.py
infrastructure/youtube/ytdlp_downloader.py
infrastructure/metadata/mutagen_metadata_writer.py
infrastructure/repositories/sqlalchemy_song_repository.py
```

---

## Ejemplo de flujo completo: sincronizar playlist de YouTube

```txt
Usuario pega URL de playlist
↓
PlaylistSyncWorker
↓
SyncYoutubePlaylistUseCase.execute(url)
↓
YtdlpPlaylistReader obtiene vídeos
↓
SongRepository obtiene canciones locales
↓
SongMatcher compara nombres
↓
PlaylistRepository guarda resultados
↓
UI muestra:
   - descargadas
   - faltantes
   - posibles coincidencias dudosas
```

Archivos implicados:

```txt
presentation/ui/playlist_sync_view.py
workers/playlist_sync_worker.py
application/use_cases/sync_youtube_playlist.py
domain/services/song_matcher.py
infrastructure/youtube/ytdlp_playlist_reader.py
infrastructure/repositories/sqlalchemy_song_repository.py
infrastructure/repositories/sqlalchemy_playlist_repository.py
```

---

## Convenciones de nombres

### Archivos

Usar snake_case:

```txt
scan_music_folder.py
download_song.py
edit_song_metadata.py
```

### Clases

Usar PascalCase:

```txt
ScanMusicFolderUseCase
DownloadSongUseCase
EditSongMetadataUseCase
```

### Variables y funciones

Usar snake_case:

```txt
song_title
download_path
scan_folder()
```

### Tests

Usar:

```txt
test_nombre_del_comportamiento.py
```

Ejemplo:

```txt
test_song_matcher_detects_same_song.py
```

---

## Convención para Use Cases

Cada Use Case debe tener un método principal:

```python
execute(...)
```

Ejemplo:

```python
class ScanMusicFolderUseCase:
    def execute(self, folder_path: str) -> list[SongDTO]:
        ...
```

---

## Convención para Repositories

Los repositories deben esconder SQLAlchemy.

La aplicación no debe saber cómo se consulta la base de datos.

Ejemplo:

```python
class SongRepository:
    def get_by_id(self, song_id: int):
        ...

    def list_all(self):
        ...

    def save(self, song):
        ...

    def update_metadata(self, song_id: int, metadata):
        ...
```

---

## Convención para Workers

Los workers deben usarse para operaciones lentas.

Ejemplos:

* Escaneo de carpeta.
* Descarga.
* Sync playlist.
* Conversión.
* Escritura masiva de metadata.

Los workers deben emitir señales hacia la UI, no actualizar widgets directamente desde hilos secundarios.

---

## Convención para errores

Usar excepciones específicas cuando tenga sentido.

Ejemplos:

```txt
InvalidYoutubeUrlError
SongFileNotFoundError
MetadataWriteError
DownloadFailedError
PlaylistReadError
```

La infraestructura puede lanzar errores técnicos.

Los Use Cases deben traducir esos errores a mensajes entendibles para la UI.

---

## Logging

Usar loguru.

Registrar:

* Inicio de app.
* Escaneos.
* Canciones encontradas.
* Descargas iniciadas/fallidas/finalizadas.
* Errores de metadata.
* Errores de base de datos.
* Errores de ffmpeg/yt-dlp.

No registrar datos sensibles innecesarios.

---

## Configuración

Toda ruta configurable debe venir de `.env` o de settings persistidos.

Ejemplos:

```txt
MUSIC_FOLDER
DOWNLOAD_FOLDER
DATABASE_URL
FFMPEG_PATH
LOG_LEVEL
```

No hardcodear rutas absolutas personales.

Incorrecto:

```txt
D:/Usuarios/Angel/Musica
```

Correcto:

```txt
MUSIC_FOLDER=D:/Music
```

---

## Base de datos

La base de datos debe guardar índices y estado de la app, no duplicar archivos.

Tabla inicial sugerida `songs`:

```txt
id
path
title
artist
album
year
track_number
duration
created_at
updated_at
```

Tablas futuras:

```txt
playlists
playlist_items
downloads
settings
favorites
playback_history
```

---

## Orden recomendado de desarrollo

### Fase 1: base del proyecto

* Crear estructura.
* Configurar PySide6.
* Configurar SQLAlchemy.
* Configurar Alembic.
* Configurar SQLite.
* Crear ventana principal.
* Crear tabla de canciones vacía.

---

### Fase 2: escaneo de música

* Escanear carpeta.
* Detectar MP3.
* Leer metadata con Mutagen.
* Guardar canciones en SQLite.
* Mostrar canciones en tabla.

---

### Fase 3: reproducción

* Reproducir canción.
* Pausar.
* Stop.
* Barra de progreso.
* Volumen.
* Siguiente/anterior.

---

### Fase 4: editor de metadata

* Abrir editor.
* Modificar título.
* Modificar artista.
* Modificar álbum.
* Modificar año.
* Modificar track.
* Cambiar carátula.
* Guardar en MP3.
* Actualizar SQLite.

---

### Fase 5: descargas

* Pegar URL.
* Descargar audio.
* Convertir a MP3.
* Guardar en carpeta configurada.
* Leer metadata resultante.
* Insertar en SQLite.

---

### Fase 6: playlists YouTube

* Leer playlist.
* Guardar items.
* Comparar con biblioteca local.
* Mostrar descargadas/faltantes.
* Permitir descargar faltantes.

---

### Fase 7: mejoras

* Favoritos.
* Historial.
* Búsqueda avanzada.
* Duplicados.
* Normalización de nombres.
* Exportar playlist.
* Empaquetar con PyInstaller.

---

## Qué no hacer

No hacer esto:

* Meter toda la lógica en `main_window.py`.
* Consultar SQLite desde la UI.
* Ejecutar yt-dlp desde botones.
* Escribir metadata desde widgets.
* Guardar carátulas en la base de datos.
* Añadir Django, Flask o FastAPI.
* Añadir MySQL al principio.
* Añadir Cloudinary.
* Crear caché permanente de imágenes desde el inicio.
* Crear arquitectura enterprise innecesaria.
* Meter lógica de negocio en `utils`.

---

## Regla principal

Cada vez que se añada algo nuevo, preguntarse:

```txt
¿Esto es UI?
→ presentation

¿Esto es una acción del usuario?
→ application/use_cases

¿Esto es una regla pura del negocio?
→ domain

¿Esto toca archivos, DB, yt-dlp, ffmpeg, Mutagen o HTTP?
→ infrastructure

¿Esto tarda y puede congelar la interfaz?
→ workers
```

---

## Filosofía del proyecto

La app debe crecer de forma ordenada.

Prioridad:

1. Código claro.
2. Separación de responsabilidades.
3. UI sin lógica pesada.
4. Infraestructura aislada.
5. Use Cases fáciles de entender.
6. Dominio simple, no sobreingeniería.
7. SQLite como base local.
8. MP3 como fuente real de metadatos.
9. Tests en partes importantes.
10. Empaquetado al final.
