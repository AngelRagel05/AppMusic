# Tkinter Theming

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Objetivo

Definir como escalar el sistema visual de `Tkinter` cuando el proyecto tenga muchas pantallas con identidad distinta.

---

## Regla base

No crear estilos ad hoc dentro de cada pagina como primera opcion.

La jerarquia recomendada es:

1. `BASE_THEME` como identidad global
2. `PAGE_THEME_OVERRIDES` para variaciones por pantalla
3. `widgetFactory.py` para widgets reutilizables
4. overrides locales solo cuando un componente lo necesite de verdad

---

## Estructura

```txt
app/presentation/uiTheme/
├─ themePalette.py
├─ widgetFactory.py
├─ windowStyler.py
└─ signalSupport.py
```

`themePalette.py` contiene:

* `BASE_THEME`
* `PAGE_THEME_OVERRIDES`
* `mergeTheme(...)`
* `getPageTheme(...)`

---

## Patron recomendado para paginas

Cada pagina resuelve su tema una sola vez:

```python
self._theme = getPageTheme("libraries")
```

Y despues pasa ese tema a sus componentes hijos:

```python
self.header = PageHeader(self, "Biblioteca local", self._theme)
self.section = LocalLibrariesSection(self, self._theme)
```

Esto evita que cada subcomponente tome decisiones visuales incompatibles.

---

## Si tienes 40 paginas distintas

No hagas 40 sistemas de estilo independientes.

Haz esto:

* mantén un `BASE_THEME` comun
* define una entrada por pagina o familia de paginas en `PAGE_THEME_OVERRIDES`
* comparte factories de botones, labels, inputs y estados
* cambia solo tokens, no el mecanismo de renderizado

Ejemplo conceptual:

```python
PAGE_THEME_OVERRIDES = {
    "overview": {},
    "libraries": {"accent": "#4D9F70"},
    "playlists": {"accent": "#D86C3F"},
    "filters": {"accent": "#8B7CF6"},
}
```

Si en el futuro hay 40 paginas pero solo 5 familias visuales, usa 5 temas de familia y no 40 temas unicos.

---

## Cuando una pagina necesita un look muy distinto

Si una pantalla necesita una identidad casi propia:

* crea un override fuerte con `getPageTheme("miPagina", overrides)`
* encapsula widgets propios en su carpeta de feature
* conserva nombres de tokens comunes como `bg`, `surface`, `accent`, `text`

No cambies la API de los factories para cada pagina nueva.

---

## Regla de escalabilidad

Si una necesidad visual puede resolverse tocando tokens, no dupliques componentes.

Duplica un widget solo cuando cambie:

* la estructura
* el comportamiento
* o la semantica del componente

No lo dupliques solo porque cambie de verde a naranja.
