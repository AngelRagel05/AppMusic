# UI Component Structure

## Objetivo

Definir una convencion simple y explicita para organizar componentes visuales en `app/presentation/ui/`.

---

## Regla general

Cada componente visual debe vivir en su propia carpeta y agrupar como minimo:

```txt
componentName/
└─ componentName.py
```

Ejemplos:

```txt
app/presentation/ui/localLibraries/
└─ localLibrariesSection.py

app/presentation/ui/ignoredTerms/
└─ ignoredTermsSection.py

app/presentation/ui/youtubePlaylists/
└─ youtubePlaylistsSection.py
```

Cuando un componente crezca demasiado y mezcle composicion, coordinacion de eventos y
sincronizacion de datos, no se deben anadir helpers sueltos dentro de su carpeta base.

La regla sigue siendo estricta:

* cada componente visual tiene su propia carpeta
* cada carpeta de componente visual contiene su modulo principal `.py`
* si un componente necesita soporte adicional, debe usarse un helper local o la capa compartida de presentacion, no una hoja de estilos paralela por defecto
* cuando varios componentes pertenezcan a una misma pantalla o feature, deben agruparse bajo una carpeta padre con nombre de feature
* los helpers no visuales deben salir de `app/presentation/ui/`

Ejemplo valido:

```txt
app/presentation/
├─ shell/
│  ├─ appShell/
│  │  └─ appShell.py
│  ├─ mainWindow/
│  │  └─ mainWindow.py
│  └─ sidebar/
│     ├─ sidebar/
│     │  └─ sidebar.py
│     ├─ brandPanel/
│     │  └─ brandPanel.py
│     ├─ navigationMenu/
│     │  └─ navigationMenu.py
│     ├─ contextSummary/
│     │  └─ contextSummary.py
│     └─ navigationFooter/
│        └─ navigationFooter.py
├─ shared/
│  ├─ theme/
│  │  ├─ signalSupport.py
│  │  ├─ themePalette.py
│  │  ├─ widgetFactory.py
│  │  └─ windowStyler.py
│  └─ widgets/
│     ├─ dataTable/
│     │  └─ dataTable.py
│     ├─ pageHeader/
│     │  └─ pageHeader.py
│     ├─ statCard/
│     │  └─ statCard.py
│     └─ statusBadge/
│        └─ statusBadge.py
└─ features/
   ├─ overview/
   │  └─ ui/
   │     └─ overviewPage/
   │        ├─ overviewPage.py
   │        └─ dashboardView.py
   ├─ localLibrary/
   │  ├─ controller/
   │  │  └─ localLibraryController.py
   │  ├─ viewmodel/
   │  │  └─ localFolderViewModel.py
   │  └─ ui/
   │     └─ localLibraryPage/
   │        ├─ localLibraryPage.py
   │        └─ localLibrariesSection/
   │           └─ localLibrariesSection.py
   ├─ youtubePlaylists/
   │  ├─ controller/
   │  │  └─ youtubePlaylistsController.py
   │  ├─ viewmodel/
   │  │  └─ youtubePlaylistViewModel.py
   │  └─ ui/
   │     └─ youtubePlaylistsPage/
   │        ├─ youtubePlaylistsPage.py
   │        └─ youtubePlaylistsSection/
   │           └─ youtubePlaylistsSection.py
   └─ ignoredTerms/
      ├─ controller/
      │  └─ ignoredTermsController.py
      ├─ viewmodel/
      │  └─ ignoredTermsViewModel.py
      └─ ui/
         └─ ignoredTermsPage/
            ├─ ignoredTermsPage.py
            └─ ignoredTermsSection/
               └─ ignoredTermsSection.py
```

---

## Regla sobre `__init__.py`

Las carpetas hijas de componentes dentro de `app/presentation/ui/` no deben llevar `__init__.py` salvo que exista una necesidad real de exponer una API publica de paquete.

Motivos:

* reduce ruido visual en una estructura basada en componentes pequenos
* evita reexports innecesarios
* hace que el origen real de cada clase o helper sea explicito

Se puede mantener `__init__.py` en carpetas padre cuando aporte valor estructural o de entrada al modulo.

---

## Regla de imports

Los imports de UI deben ser explicitos y apuntar al modulo real.

Correcto:

```python
from app.presentation.ui.localLibraries.localLibrariesSection import LocalLibrariesSection
from app.presentation.ui.ignoredTerms.ignoredTermsSection import IgnoredTermsSection
from app.presentation.ui.shared.dataTable import configureDataTable
```

Evitar:

```python
from app.presentation.ui.localLibraries import LocalLibrariesSection
from app.presentation.ui.shared import configureDataTable
```

---

## Beneficios

* mejor trazabilidad del origen de cada dependencia
* menos ficheros accesorios por componente
* estructura mas limpia para componentes pequenos y reutilizables
* menor acoplamiento a reexports de paquete

## Regla adicional para `shared/`

`shared/` no es un cajon general.

Solo debe contener:

* tema visual reutilizable
* widgets realmente compartidos entre varias features o el shell

Si un componente solo se usa en una pantalla o depende de reglas concretas de una feature, debe salir de `shared/` y vivir dentro de esa feature.
