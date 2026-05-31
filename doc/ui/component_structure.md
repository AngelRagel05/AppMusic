# UI Component Structure

## Objetivo

Definir una convencion simple y explicita para organizar componentes visuales en `app/presentation/ui/`.

---

## Regla general

Cada componente visual debe vivir en su propia carpeta y agrupar como minimo:

```txt
componentName/
├─ componentName.py
└─ componentName.qss
```

Ejemplos:

```txt
app/presentation/ui/localLibraries/
├─ localLibrariesSection.py
└─ localLibrariesSection.qss

app/presentation/ui/ignoredTerms/
├─ ignoredTermsSection.py
└─ ignoredTermsSection.qss
```

Cuando un componente crezca demasiado y mezcle composicion, coordinacion de eventos y
sincronizacion de datos, no se deben anadir helpers sueltos dentro de su carpeta base.

La regla sigue siendo estricta:

* cada componente visual tiene su propia carpeta
* cada carpeta de componente visual contiene su pareja `.py` y `.qss`
* en un mismo nivel no pueden convivir archivos `.py` y `.qss` de un componente con subcarpetas de otros componentes
* cuando varios componentes pertenezcan a una misma pantalla o feature, deben agruparse bajo una carpeta padre con nombre de feature
* los helpers no visuales deben salir de `app/presentation/ui/`

Ejemplo valido:

```txt
app/presentation/ui/mainScreen/
├─ mainWindow/
│  ├─ mainWindow.py
│  └─ mainWindow.qss
├─ heroSection/
│  ├─ heroSection.py
│  └─ heroSection.qss
└─ mainWindowPage/
   ├─ mainWindowPage.py
   └─ mainWindowPage.qss
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
