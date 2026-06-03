# Tabla `local_song`

## Nombre

`local_song`

## Objetivo

Representa una cancion existente en disco dentro de una carpeta local.

Es la fuente local que se compara contra los items de YouTube.

## Columnas

| Columna | Tipo conceptual | Requerido | Restricciones | Descripcion |
| --- | --- | --- | --- | --- |
| `id` | entero | si | PK | Identificador unico |
| `local_folder_id` | entero | si | FK | Carpeta local a la que pertenece |
| `download_id` | entero | no | FK | Descarga que origino la cancion |
| `file_path` | texto | si | UNIQUE | Ruta completa del archivo |
| `file_name` | texto | si | - | Nombre del archivo |
| `title` | texto | si | - | Titulo de la cancion |
| `artist` | texto | si | - | Artista principal |
| `album` | texto | si | - | Album; si no hay tag se guarda vacio |
| `release_year` | entero | si | - | Año de lanzamiento; si no hay tag se guarda `0` |
| `track_number_album` | entero | si | - | Numero de pista dentro del album; si no hay tag se guarda `0` |
| `duration_seconds` | decimal | si | - | Duracion en segundos; si no puede calcularse se guarda `0.0` |
| `created_at` | fecha-hora | si | - | Fecha de creacion |
| `updated_at` | fecha-hora | si | - | Fecha de ultima actualizacion |

## Relaciones

* cada `local_song` pertenece a una sola `local_folder`
* una `local_song` puede provenir de una `download`
* una `local_song` puede aparecer en muchos `playlist_comparison_result`

## Diagrama Mermaid

```mermaid
erDiagram
    local_song {
        int id PK
        int local_folder_id FK
        int download_id FK
        string file_path UK
        string file_name
        string title
        string artist
        string album
        int release_year
        int track_number_album
        float duration_seconds
        datetime created_at
        datetime updated_at
    }

    local_folder {
        int id PK
    }

    download {
        int id PK
    }

    playlist_comparison_result {
        int id PK
        int local_song_id FK
    }

    local_folder ||--|{ local_song : contiene
    download o|--o| local_song : genera
    local_song o|--o{ playlist_comparison_result : coincide_con
```

## Notas

* `file_path` debe ser unico para impedir duplicados fisicos.
* En la carpeta local no deben existir canciones repetidas como regla de negocio.
* Durante el escaneo local, `file_path` y `file_name` se obtienen del filesystem.
* `title`, `artist`, `album`, `release_year`, `track_number_album` y `duration_seconds` se intentan extraer con `Mutagen`.
* Si el MP3 no tiene tags o falla la lectura de metadata, la app usa fallback seguro:
  * `title`: nombre del archivo sin extension
  * `artist`: cadena vacia
  * `album`: cadena vacia
  * `release_year`: `0`
  * `track_number_album`: `0`
  * `duration_seconds`: `0.0`
