# Tabla `playlist_comparison`

## Nombre

`playlist_comparison`

## Objetivo

Representa una ejecucion de comparacion entre una playlist de YouTube y una carpeta local.

Actua como cabecera del proceso de comparacion.

## Columnas

| Columna | Tipo conceptual | Requerido | Restricciones | Descripcion |
| --- | --- | --- | --- | --- |
| `id` | entero | si | PK | Identificador unico |
| `youtube_playlist_id` | entero | si | FK | Playlist comparada |
| `local_folder_id` | entero | si | FK | Carpeta local comparada |
| `compared_at` | fecha-hora | si | - | Momento real de la comparacion |
| `created_at` | fecha-hora | si | - | Fecha de creacion del registro |

## Relaciones

* cada `playlist_comparison` pertenece a una `youtube_playlist`
* cada `playlist_comparison` pertenece a una `local_folder`
* una `playlist_comparison` produce muchos `playlist_comparison_result`

## Diagrama Mermaid

```mermaid
erDiagram
    playlist_comparison {
        int id PK
        int youtube_playlist_id FK
        int local_folder_id FK
        datetime compared_at
        datetime created_at
    }

    youtube_playlist {
        int id PK
    }

    local_folder {
        int id PK
    }

    playlist_comparison_result {
        int id PK
        int playlist_comparison_id FK
    }

    youtube_playlist ||--|{ playlist_comparison : genera
    local_folder ||--|{ playlist_comparison : se_compara_con
    playlist_comparison ||--|{ playlist_comparison_result : produce
```

## Notas

* Normalmente se genera una nueva comparacion al abrir la app y ejecutar la revision.
