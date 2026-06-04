# Tabla `download`

## Nombre

`download`

## Objetivo

Representa un intento de descarga iniciado desde un item de playlist de YouTube hacia una carpeta local.

## Columnas

| Columna | Tipo conceptual | Requerido | Restricciones | Descripcion |
| --- | --- | --- | --- | --- |
| `id` | entero | si | PK | Identificador unico |
| `youtube_playlist_item_id` | entero | si | FK | Item de YouTube origen |
| `local_folder_id` | entero | si | FK | Carpeta destino |
| `source_url` | texto | si | - | URL origen de la descarga |
| `status` | texto | si | - | Estado de la descarga |
| `target_file_path` | texto | no | - | Ruta final esperada o generada |
| `error_message` | texto | no | - | Detalle del error si falla |
| `started_at` | fecha-hora | no | - | Momento de inicio |
| `finished_at` | fecha-hora | no | - | Momento de fin |
| `created_at` | fecha-hora | si | - | Fecha de creacion |
| `updated_at` | fecha-hora | si | - | Fecha de ultima actualizacion |

## Relaciones

* cada `download` nace de un `youtube_playlist_item`
* cada `download` apunta a una `local_folder`
* un `download` puede generar una `local_song`

## Diagrama Mermaid

```mermaid
erDiagram
    download {
        int id PK
        int youtube_playlist_item_id FK
        int local_folder_id FK
        string source_url
        string status
        string target_file_path
        string error_message
        datetime started_at
        datetime finished_at
        datetime created_at
        datetime updated_at
    }

    youtube_playlist_item {
        int id PK
    }

    local_folder {
        int id PK
    }

    local_song {
        int id PK
        int download_id FK
    }

    youtube_playlist_item ||--o{ download : origina
    local_folder ||--o{ download : descarga_en
    download o|--o| local_song : genera
```

## Notas

* `status` debe usar este catalogo inicial:
  * `pending`
  * `in_progress`
  * `completed`
  * `failed`
* `youtube_playlist_item` no guarda ya una URL de video canonica; `source_url` se resuelve en el flujo de descarga a partir del item importado y su identificador externo.
* La lista de errores posibles debe vivir en codigo.
* `error_message` solo guarda el detalle concreto del fallo ocurrido.
