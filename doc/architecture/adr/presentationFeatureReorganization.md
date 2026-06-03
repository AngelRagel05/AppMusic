# ADR: Reorganizacion de `presentation` por features

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

La ADR de presentacion modular para `Tkinter` ya fijaba el criterio `shell + shared + features`, pero la estructura fisica todavia conservaba restos de la etapa anterior:

* `controllers/` global
* `viewmodels/` global
* `ui/mainScreen/` mezclando shell, paginas y componentes compartidos

Eso provocaba una estructura hibrida donde la organizacion real del codigo no coincidia con la arquitectura aprobada.

## Decision

Se reorganiza `app/presentation/` en tres zonas explicitas:

```txt
app/presentation/
├─ shell/
├─ shared/
└─ features/
```

### `shell/`

Contiene navegacion y armazon global:

* `mainWindow/`
* `appShell/`
* `sidebar/`

### `shared/`

Contiene componentes visuales reutilizables:

* `widgets/pageHeader/`
* `widgets/statCard/`
* `widgets/statusBadge/`

### `features/`

Cada modulo funcional agrupa su propio subarbol:

* `overview/`
* `localLibrary/`
* `youtubePlaylists/`
* `ignoredTerms/`

Cada feature puede contener:

```txt
featureName/
├─ controller/
├─ viewmodel/
└─ ui/
```

## Consecuencias

Ventajas:

* la estructura fisica coincide con la arquitectura documentada
* cada feature queda localizada en una sola zona
* el shell deja de depender del arbol antiguo de `mainScreen`
* resulta mas facil seguir creciendo sin volver a carpetas globales por tipo tecnico

Costes:

* hay que actualizar imports y nombres de navegacion internos
* algunos nombres visuales pueden seguir siendo de negocio mientras se completa la limpieza fina

## Notas

Esta fase no sustituye todavia `uiTheme/`.

Ese soporte transversal sigue vivo de forma temporal y su reorganizacion queda separada del movimiento principal de shell, shared y features.
