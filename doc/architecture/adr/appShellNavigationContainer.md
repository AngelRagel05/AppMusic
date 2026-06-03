# ADR: `AppShell` como contenedor de navegacion

## Estado

Historico

## Regla de vigencia

Si entra en conflicto con la documentacion canónica, prevalece la documentacion canónica.

## Estado

Aprobada

## Fecha

2026-06-03

## Contexto

Tras separar `presentation` en `shell + shared + features`, el shell seguia exponiendo propiedades agregadas de detalle como:

* `localLibrariesSection`
* `youtubePlaylistsSection`
* `ignoredTermsSection`

Ademas, los controllers de feature recibian `MainWindow` y navegaban por todo el arbol del shell para llegar a sus widgets internos.

## Decision

`AppShell` queda reducido a contenedor de navegacion y coordinacion de paginas.

Reglas:

* `AppShell` conoce paginas raiz de feature, no secciones internas
* cada controller recibe su propia vista raiz de feature
* la navegacion entre paginas se expone como callback explicito
* los updates de estado compartido se propagan mediante callbacks dedicados, no recorriendo el arbol del shell

## Consecuencias

Ventajas:

* menos acoplamiento entre shell y features
* los controllers dejan de depender de `MainWindow`
* cada feature expone una API de presentacion propia y mas estable

Costes:

* las paginas raiz necesitan algunos metodos de fachada hacia sus widgets internos

## Nota

Esta decision no elimina la coordinacion central del shell.

Solo limita su responsabilidad a:

* mostrar paginas
* mantener estado visual compartido
* conectar navegacion global
